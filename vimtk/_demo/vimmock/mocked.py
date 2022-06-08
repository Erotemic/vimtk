r"""

Place this script in your the vimrc to inspect attributes of the real vim
python module. This can be used to make this module more accurately reflect the
real vim object.

python << endpython

def attrinfo(basename, base, attrname):
    attr = getattr(base, attrname)
    print('\n------')
    print('%s.%s: %r' % (basename, attrname, attr))
    print('type(%s.%s): %r' % (basename, attrname, type(attr)))
    print('dir(%s.%s): %r' % (basename, attrname, dir(attr)))

print('\n\n VIM BASE')
print('vim = %r' % (vim,))
print('type(vim) = %r' % (type(vim),))
print('dir(vim) = %r' % (dir(vim),))

print('\n\n VIM CURRENT')
attrinfo('vim', vim, 'current')
attrinfo('vim.current', vim.current, 'tabpage')
attrinfo('vim.current', vim.current, 'line')
attrinfo('vim.current', vim.current, 'window')
attrinfo('vim.current', vim.current, 'range')

attrinfo('vim.current', vim.current, 'buffer')

attrinfo('vim.current.buffer', vim.current.buffer, 'number')
attrinfo('vim.current.buffer', vim.current.buffer, 'name')
attrinfo('vim.current.buffer', vim.current.buffer, 'options')
attrinfo('vim.current.buffer', vim.current.buffer, 'range')
attrinfo('vim.current.buffer', vim.current.buffer, 'valid')
attrinfo('vim.current.buffer', vim.current.buffer, 'vars')
attrinfo('vim.current.buffer', vim.current.buffer, 'mark')

endpython
"""


class VimErrorMock(Exception):
    pass


class LineMock(object):
    pass


def classname(obj):
    return obj.__class__.__name__


import ubelt as ub  # NOQA


class BufferMock(ub.NiceRepr):
    """
    Attributes of the REAL vim.buffer object
        ['__dir__', '__members__', 'append', 'mark', 'name', 'number', 'options',
        'range', 'valid', 'vars']
    """
    def __init__(self, text=None):
        self._lines = None
        self.name = ''

        self.number = 1
        self.range = RangeMock
        self.valid = False
        # self.options = OptionsMock
        # self.vars = DictionaryMock()

        # maps from mark chars to positions
        self._marked_lines = {}  # type : Dict[str: Tuple[int, int]]

        self.setup_text(text)

    def __nice__(self):
        return self.name

    def _setmark(self, key, pos):
        self._marked_lines[key] = pos

    def _visual_select(self, row1, row2, col1=0, col2=None):
        """
        first and last line to select inclusive
        """
        assert row1 > 0
        assert row2 > 0
        if col2 is None:
            # col2 = len(self[row2 - 1]) - 1
            import sys
            col2 = sys.maxsize - 1
        self._setmark('<', (row1, col1))
        self._setmark('>', (row2, col2))

    def mark(self, key):
        """
        Return the 1-based line number of a mark
        """
        return self._marked_lines.get(key, None)

    @property
    def _text(self):
        return '\n'.join(self._lines)

    def __delitem__(self, key):
        del self._lines[key]

    def __getitem__(self, key):
        # Note indexing into a buffer is zero indexed like normal
        # However remember reported cursor positions are 1 indexed
        if isinstance(key, slice):
            return self._lines[key.start : key.stop : key.step]
        if not isinstance(key, int):
            raise TypeError("Index should be integer, not %s" % classname(key))
        return self._lines[key]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self._lines[key.start : key.stop : key.step] = value
        elif not isinstance(key, int):
            raise TypeError("Indes should be integer, not %s" % classname(key))
        self._lines[key] = value

    def __len__(self):
        return len(self._lines)

    def setup_text(self, text=None, name=''):
        text = text or ''
        self._lines = text.splitlines()
        self.valid = True
        self.name = name

    def open_file(self, filepath):
        with open(filepath, 'r') as file_:
            self._lines = file_.read().splitlines()
        self.valid = True
        self.name = filepath

    def append(self, other):
        """ the vim buffer append is actually an extend call """
        self._lines.extend(other)


class WindowMock(object):
    """"
    RealObjectInfo:
        vim.current.window: <window 0>
        type(vim.current.window): <type 'vim.window'>
        dir(vim.current.window): ['__dir__', '__members__', 'buffer', 'col',
            'cursor', 'height', 'number', 'options', 'row', 'tabpage', 'valid',
            'vars']
    """
    def __init__(self, cursor=None):
        # Note: weirdly rows are 1 indexed by columns are 0 indexed
        self.cursor = cursor or (1, 0)


class RangeMock(object):
    """
    RealObjectInfo:
        vim.current.range: <range  (1:1)>
        type(vim.current.range): <type 'vim.range'>
        dir(vim.current.range): ['__dir__', '__members__', 'append', 'end', 'start']
    """
    pass


class TabPageMock(object):
    """
    RealObjectInfo:
        vim.current.tabpage: <tabpage 0>
        type(vim.current.tabpage): <type 'vim.tabpage'>
        dir(vim.current.tabpage): ['__dir__', '__members__', 'number', 'valid',
                                   'vars', 'window', 'windows']
    """
    pass


class CurrentMock(object):
    """
    RealObjectInfo:
        vim.current: <vim.currentdata object at 0x8718a0>
        type(vim.current): <type 'vim.currentdata'>
        dir(vim.current): ['__dir__', '__members__', 'buffer', 'line', 'range', 'tabpage', 'window']
    """
    def __init__(self, text=None):
        self.line = LineMock()
        self.buffer = BufferMock(text)
        self.window = WindowMock()
        self.range = RangeMock()
        self.tabpage = TabPageMock()


class VimMock(object):
    """

    The real vim module is defined in the c source code (if_python.c,
    if_python3.c, if_py_both.h, etc...) in the vim package.  Therefore it is difficult to
    replicate its behavior exactly.

    vim = <module 'vim' (built-in)>
    type(vim) = <type 'module'>

    The Attributes of the REAL vim module are:
    {
         # Vim Types
        'Buffer': vim.buffer,
        'Dictionary': vim.dictionary,
        'Function': vim.function,
        'List': vim.list,
        'Options': vim.options,
        'Range': vim.range,
        'TabPage': vim.tabpage,
        'Window': vim.window,
        '_Loader': vim.Loader,

        # Members of numeric_constant
        'VAR_DEF_SCOPE': 2,
        'VAR_FIXED': 2,
        'VAR_LOCKED': 1,
        'VAR_SCOPE': 1,
        'VIM_SPECIAL_PATH': '_vim_path_',

        # Members of object_constant
        'buffers': <vim.bufferlist object at 0x8718d0>,
        'windows': <vim.windowlist object at 0x8718b0>,
        'current': <vim.currentdata object at 0x8718a0>,
        'tabpages': <vim.tabpagelist object at 0x871890>,

         # The vim module definitions
        'command': <built-in function command>,
        'eval': <built-in function eval>,
        'bindeval': <built-in function bindeval>,
        'strwidth': <built-in function strwidth>,
        'chdir': <built-in function chdir>,
        'fchdir': <built-in function fchdir>,
        'foreach_rtp': <built-in function foreach_rtp>,
        'find_module': <built-in function find_module>,
        'path_hook': <built-in function path_hook>,
        '_get_paths': <built-in function _get_paths>,

        # Python versions of redefined functions
        '_chdir': <built-in function chdir>,
        '_fchdir': <built-in function fchdir>,
        '_find_module': <built-in function find_module>,
        '_getcwd': <built-in function getcwd>,
        '_load_module': <built-in function load_module>,

        # Checked objects
        'options': <vim.options object at 0x7fae81970c30>,
        'vars': <vim.dictionary object at 0x7fae8196dc90>,
        'vvars': <vim.dictionary object at 0x7fae8196dcc0>,

        # Error definition
        'error': vim.error,

        '__doc__': None,
        '__name__': 'vim',
        '__package__': None,

        # The module also defines these attributes, but they are just imprted from
        # other places
        'os': <module 'os' from '/usr/lib/python2.7/os.pyc'>,
        }
    """
    VAR_DEF_SCOPE = 2
    VAR_FIXED = 2
    VAR_LOCKED = 1
    VAR_SCOPE =  1
    VIM_SPECIAL_PATH = '_vim_path_'

    Buffer = BufferMock
    Range = RangeMock
    TabPage = TabPageMock
    Window = WindowMock
    # Dictionary = vim.dictionary
    # Function = vim.function
    # List = vim.list
    # Options = vim.options
    # _Loader = vim.Loader

    error = VimErrorMock

    vim_mode_codes = {
        'n'  : 'Normal',
        'no' : 'NOperatorPending',
        'v'  : 'Visual',
        'V'  : 'VLine',
        #'^V' : 'VBlock',
        's'  : 'Select',
        'S'  : 'SLine',
        #'^S' : 'SBlock',
        'i'  : 'Insert',
        'R'  : 'Replace',
        'Rv' : 'VReplace',
        'c'  : 'Command',
        'cv' : 'VimEx',
        'ce' : 'Ex',
        'r'  : 'Prompt',
        'rm' : 'More',
        'r?' : 'Confirm',
        '!'  : 'Shell',
    }

    def __init__(self):
        self.current = CurrentMock()

        self.buffers = [self.current.buffer]  # vim.bufferlist
        self.windows = [self.current.window]  # vim.bufferlist
        self.tabpages = [self.current.tabpage]  # vim.tabpagelist

        self.global_variables = {}
        self._function_stack = []
        self._mode = 'n'

    def _push_function_stack(self, name, named={}, positional=[]):
        """
        Simulate being inside a vim function
        """
        stack_frame = {
            'func_name': name,
            # The args is put in a variable named "a"
            # https://learnvim.irian.to/vimscript/vimscript_functions
            # TODO: figure out and mock the exact behavior
            # This it the a: scope
            'args': {
                'positional': positional,
                'named': named,
            }
        }
        self._function_stack.append(stack_frame)

    def setup_text(self, text, name=''):
        """
        special mock-only function to put text into the buffer
        """
        self.current.buffer.setup_text(text, name)

    def move_cursor(self, row, col=0):
        """
        Move the cursor to a particular row / column

        Note:
            rows are 1 indexed but columns are 0 indexed
        """
        if row <= 0:
            raise Exception('rows are 1 indexed')
        if col < 0:
            raise Exception('cols are 0 indexed')
        self.current.window.cursor = (row, col)

    def open_file(self, filepath, cursor=None):
        """
        special mock-only function to put text into the buffer
        """
        # Create a buffer and set it as the current buffer
        new_buffer = BufferMock()
        new_buffer.open_file(filepath)
        self.buffers.append(new_buffer)
        self.current.buffer = new_buffer
        self.current.window.cursor = cursor or (0, 0)

    def command(self, command):
        """
        Hack that pretends to "execute" a vim command
        """

        if command == 'ESC':
            # Switch to normal mode
            self._mode = 'n'
        else:
            raise NotImplementedError(command)

    def eval(self, command):
        """
        A very hack, and very specific implementation of vim eval for tests.

        This only handles very specific commands.
        """
        # print('command = {!r}'.format(command))
        if command == '&ft':
            from os.path import splitext
            return splitext(self.current.buffer.name)[1].lstrip('.')

        if command == 'mode()':
            return self._mode

        if command.startswith('let '):
            return self._eval_assignment(command)

        if command.startswith('exists(') and command.endswith(')'):
            arg = command[8:-2]
            return arg in self.global_variables

        if command.startswith('get(') and command.endswith(')'):
            inner = command[4:-1]
            context, arg = inner.split(':, ')
            varkey = arg.strip('"')
            varname = '{}:{}'.format(context, varkey)
            return self.global_variables[varname]

        hard_coded_commands = {
            'jedi#_vim_exceptions("&encoding", 1)': {'result': 'utf-8'},
            '&encoding': 'utf-8',
            ':set nofoldenable': '',
        }
        if command in hard_coded_commands:
            return hard_coded_commands[command]

        if command.startswith('a:'):
            # raise a vim.error if the variable does not exist
            if not self._function_stack:
                raise self.error('Vim:E121: Undefined variable: {}'.format(command))

            # Probably trying to grab a function arg
            # https://learnvimscriptthehardway.stevelosh.com/chapters/24.html
            # https://learnvim.irian.to/vimscript/vimscript_variable_scopes#variable-scopes
            suffix = command[2:]
            try:
                index = int(suffix)
            except Exception:
                index = NotImplemented

            if isinstance(index, int):
                stack_frame = self._function_stack[-1]
                argv = stack_frame['args']['positional']
                if index == 0:
                    return len(argv)
                else:
                    return argv[index - 1]
            else:
                raise NotImplementedError('only positional for now')

        raise NotImplementedError('eval not generally implemented for {}'.format(command))
        # maybe :e will call open_file?

    def _eval_assignment(self, command):
        """

        References:
            * https://github.com/vim-jp/vim-vimlparser
            * https://github.com/Vimjas/vint/blob/master/vint/ast/parsing.py

        Ignore:
            # TODO: use a real vim parser
            from vint.ast import parsing
            parser = parsing.Parser()
            tree = parser.parse("let g:myvar = ['a', 'b', 'c']")
            tree['body'][0]['right']['value']

            command = "let g:myvar = ['a', 'b', 'c']"
        """
        prefix = 'let '
        assert command.startswith(prefix)
        remain = command[len(prefix):]
        lhs, rhs = remain.split('=', 1)
        lhs = lhs.strip()
        rhs = rhs.strip()

        context = None
        varname = lhs
        if ':' in lhs:
            context, key = varname.split(':', 1)

        assert context == 'g', 'only globals supported for now'

        import ast
        varvalue = ast.literal_eval(rhs)
        self.global_variables[varname] = varvalue
