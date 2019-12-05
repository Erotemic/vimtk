import itertools as it
from os.path import join
from os.path import isdir
from os.path import exists
from os.path import expanduser
import re
import sys
import logging
try:
    import ubelt as ub
except Exception:
    print('\nsys.prefix = {}\n'.format(sys.prefix))
    raise
from vimtk import xctrl
from vimtk import cplat

logger = logging.getLogger(__name__)


def __setup_logger():
    # TODO: setting up logging should be handled by the vim plugin
    # global loggers in python modules should not log anywhere by default
    global logger

    # logger.propagate = False

    # Remove existing handlers
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # By default loggers write to stderr, but we want to write to stdout
    # so vim doesn't interpret logs as errors
    fmtr = logging.Formatter('%(levelname)s: %(message)s')

    hdlr = logging.StreamHandler(sys.stdout)
    hdlr.setFormatter(fmtr)
    hdlr.setLevel(logging.INFO)
    # hdlr.setLevel(logging.DEBUG)

    logger.addHandler(hdlr)

__setup_logger()

# logger.basicConfig()
# logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


def reload_vimtk():
    """
    Used for development
    """
    try:
        import importlib
        reload = importlib.reload
    except (AttributeError, ImportError):
        import imp
        reload = imp.reload
        logger.debug('Reloading vimtk')
    import vimtk
    import vimtk.core
    import vimtk.xctrl
    import vimtk.pyinspect
    import vimtk.cplat

    reload(vimtk.pyinspect)
    reload(vimtk.cplat)
    reload(vimtk.core)
    reload(vimtk.xctrl)
    reload(vimtk)

    import ubelt as ub
    if ub.WIN32:
        import vimtk.win32_ctrl
        reload(vimtk.win32_ctrl)


reload = reload_vimtk


class Config(object):
    """
    Query the state of the vim variable namespace.
    """
    def __init__(self):
        self.default = {
            'vimtk_terminal_pattern': None,
            'vimtk_multiline_num_press_enter': 3,
            'vimtk_auto_importable_modules': {
                'it': 'import itertools as it',
                'nh': 'import netharn as nh',
                'np': 'import numpy as np',
                'pd': 'import pandas as pd',
                'ub': 'import ubelt as ub',
                'nx': 'import networkx as nx',
                'Image': 'from PIL import Image',
                'mpl': 'import matplotlib as mpl',
                'nn': 'from torch import nn',
                'torch_data': 'import torch.utils.data as torch_data',
                'F': 'import torch.nn.functional as F',
                'math': 'import math',
            }
        }
        self.state = self.default.copy()
        pass

    def __getitem__(self, key):
        self.getvar(key, default=self.state[key])
        return self.state[key]

    def get(self, key, default=None, context='g'):
        """ gets the value of a vim variable and defaults if it does not exist """
        import vim
        assert key in self.default
        varname = '{}:{}'.format(context, key)
        var_exists = int(vim.eval('exists("{}")'.format(varname)))
        if var_exists:
            value = vim.eval('get({}:, "{}")'.format(context, key))
        else:
            value = default
        return value


class Clipboard(object):
    @staticmethod
    def copy(text):
        return cplat.copy_text_to_clipboard(text)

    @staticmethod
    def paste():
        # Using pyperclip seems to freeze.
        # Access clipboard via vim instead
        try:
            import vim
            text = vim.eval('@+')
        except ImportError:
            text = cplat.get_clipboard()
        return text


class TextSelector(object):
    r"""
    Tools for selecting and reading text from Vim
    """

    @staticmethod
    def _demo_vim():
        """
        Notes:
            requires github.com:Erotemic/vimmock.git@dev/refactor

        """
        from vimtk._demo import vimmock
        vimmock.patch_vim()
        import vim
        import ubelt as ub
        vim.setup_text(ub.codeblock(
            '''
            def foo():
                return 1

            def bar():
                return 2
            '''))
        vim.move_cursor(1, 0)
        return vim

    @staticmethod
    def current_indent(url_ok=False):
        """
        Returns the indentation that should be used when inserting new lines.

        Example:
            >>> from vimtk._demo import vimmock
            >>> import ubelt as ub
            >>> import vimtk
            >>> vim = vimmock.patch_vim()
            >>> vim.setup_text(ub.codeblock(
            >>>     '''
            >>>     class Foo:
            >>>         def __init__(self):
            >>>             self.foo = 1
            >>>             self.foo = 2
            >>>     '''))
            >>> vim.move_cursor(1)
            >>> n1 = len(vimtk.TextSelector.current_indent())
            >>> vim.move_cursor(2)
            >>> n2 = len(vimtk.TextSelector.current_indent())
            >>> vim.move_cursor(3)
            >>> n3 = len(vimtk.TextSelector.current_indent())
            >>> assert (n1, n2, n3) == (4, 8, 8)
        """

        # Check current line for cues
        curr_line = TextSelector.line_at_cursor()
        curr_indent = get_minimum_indentation(curr_line)
        if curr_line is None:
            next_line = ''
        if curr_line.strip().endswith(':'):
            curr_indent += 4
        # Check next line for cues
        next_line = get_first_nonempty_line_after_cursor()
        if next_line is None:
            next_line = ''
        next_indent = get_minimum_indentation(next_line)
        if next_indent <= curr_indent + 8:
            # hack for overindented lines
            min_indent = max(curr_indent, next_indent)
        else:
            min_indent = curr_indent
        indent = (' ' * min_indent)
        if curr_line.strip().startswith('>>>'):
            indent += '>>> '
        return indent

    @staticmethod
    def word_at_cursor(url_ok=False):
        """
        returns the word highlighted by the curor

        Example:
            >>> from vimtk._demo import vimmock
            >>> import ubelt as ub
            >>> vim = vimmock.patch_vim()
            >>> vim.setup_text(ub.codeblock(
            >>>     '''
            >>>     class Foo:
            >>>         def __init__(self):
            >>>             self.foo = 1
            >>>             self.bar = 2
            >>>     '''))
            >>> vim.move_cursor(3, 14)
            >>> word = TextSelector.word_at_cursor()
            >>> print('word = {!r}'.format(word))
            word = 'self.foo'
        """
        import vim
        buf = vim.current.buffer
        (row, col) = vim.current.window.cursor
        line = buf[row - 1]  # Original end of the file
        if url_ok:
            nonword_chars_left = ' \t\n\r{},"\'\\'
            nonword_chars_right = nonword_chars_left
        else:
            nonword_chars_left  = ' \t\n\r[](){}:;,"\'\\/=$*'
            nonword_chars_right = ' \t\n\r[](){}:;,"\'\\/=$*.'
        word = TextSelector.get_word_in_line_at_col(
            line, col, nonword_chars_left=nonword_chars_left,
            nonword_chars_right=nonword_chars_right)
        return word

    @staticmethod
    def get_word_in_line_at_col(line, col,
                                nonword_chars_left=' \t\n\r[](){}:;,"\'\\/',
                                nonword_chars_right=None):
        r"""
        Args:
            line (str):
            col (int):

        CommandLine:
            python -m vimtk.core TextSelector.get_word_in_line_at_col

        Example:
            >>> line = 'myvar.foo = yourvar.foobar'
            >>> line = 'def loadfunc(self):'
            >>> col = 6
            >>> nonword_chars=' \t\n\r[](){}:;.,"\'\\/'
            >>> word = TextSelector.get_word_in_line_at_col(line, col, nonword_chars)
            >>> result = ('word = %r' % (word,))
            >>> print(result)
        """
        if nonword_chars_right is None:
            nonword_chars_right = nonword_chars_left
        lpos = col
        rpos = col
        while lpos > 0:
            # Expand to the left
            if line[lpos] in nonword_chars_left:
                lpos += 1
                break
            lpos -= 1
        while rpos < len(line):
            # Expand to the right
            if line[rpos] in nonword_chars_right:
                break
            rpos += 1
        word = line[lpos:rpos]
        return word

    @staticmethod
    def selected_text(select_at_cursor=False):
        r"""
        Returns all text in curent selection.

        make sure the vim function calling this has a range after ()

        Currently used by <ctrl+g>

        Refered to [vim_between_selection]_.

        References:
            .. [vim_between_selection] http://stackoverflow.com/questions/18165973/vim-between-selection

        SeeAlso:
            ~/local/vim/rc/custom_misc_functions.vim

        Test paragraph.
        Far out in the uncharted backwaters of the unfashionable end of the
        western spiral arm of the Galaxy lies a small unregarded yellow sun.
        Orbiting this at a distance of roughly ninety-two million miles is an
        utterly insignificant little blue green planet whose ape-descended life
        forms are so amazingly primitive that they still think digital watches
        are a pretty neat idea.
        % ---
        one. two three. four.

        CommandLine:
            xdoctest -m vimtk.core TextSelector.selected_text

        Example:
            >>> from vimtk._demo import vimmock
            >>> import ubelt as ub
            >>> vim = vimmock.patch_vim()
            >>> vim.setup_text(ub.codeblock(
            >>>     '''
            >>>     line n1
            >>>     line n2
            >>>     line n3
            >>>     line n4
            >>>     '''))
            >>> vim.move_cursor(3)
            >>> vim.current.buffer._visual_select(2, 3)
            >>> text = TextSelector.selected_text()
            >>> print(text)
            line n2
            line n3
            >>> vim.current.buffer._visual_select(2, 3, 0, 5)
            >>> text = TextSelector.selected_text()
            >>> print(text)
            line n
            line n
        """
        import vim
        logger.debug('grabbing visually selected text')
        buf = vim.current.buffer
        pos1 = buf.mark('<')
        pos2 = buf.mark('>')
        if pos1 and pos2:
            (lnum1, col1) = pos1
            (lnum2, col2) = pos2
            text = TextSelector.text_between_lines(lnum1, lnum2, col1, col2)
            return text

    @staticmethod
    def text_between_lines(lnum1, lnum2, col1=0, col2=sys.maxsize - 1):
        import vim
        # lines = vim.eval('getline({}, {})'.format(lnum1, lnum2))
        lines = vim.current.buffer[lnum1 - 1:lnum2]
        lines = [ub.ensure_unicode(line) for line in lines]
        try:
            if len(lines) == 0:
                pass
            elif len(lines) == 1:
                lines[0] = lines[0][col1:col2 + 1]
            else:
                # lines[0] = lines[0][col1:]
                # lines[-1] = lines[-1][:col2 + 1]
                for i in range(len(lines)):
                    lines[i] = lines[i][col1:col2 + 1]
            text = '\n'.join(lines)
        except Exception:
            print(ub.repr2(lines))
            raise
        return text

    @staticmethod
    def line_at_cursor():
        """
        Example:
            >>> from vimtk._demo import vimmock
            >>> import ubelt as ub
            >>> vim = vimmock.patch_vim()
            >>> vim.setup_text(ub.codeblock(
            >>>     '''
            >>>     def foo():
            >>>         return 1
            >>>     def bar():
            >>>         return 2
            >>>     '''))
            >>> vim.move_cursor(3)
            >>> line = TextSelector.line_at_cursor()
            >>> assert line == 'def bar():'
        """
        import vim
        logger.debug('grabbing text at current line')
        buf = vim.current.buffer
        (row, col) = vim.current.window.cursor
        line = buf[row - 1]
        return line


class CursorContext(object):
    """
    moves back to original position after context is done
    """
    def __init__(self, offset=0):
        self.pos = None
        self.offset = offset

    def __enter__(self):
        self.pos = Cursor.position()
        return self

    def __exit__(self, *exc_info):
        row, col = self.pos
        row += self.offset
        Cursor.move(row, col)


class Cursor(object):

    @staticmethod
    def move(row, col=0):
        """ move_cursor """
        import vim
        vim.command('cal cursor({},{})'.format(row, col))

    @staticmethod
    def position():
        """ get_cursor_position """
        import vim
        (row, col) = vim.current.window.cursor
        return row, col


class TextInsertor(object):
    """
    Tools for inserting text at various positions
    """

    @staticmethod
    def insert_at(text, pos):
        import vim
        # lines = [line.encode('utf-8') for line in text.split('\n')]
        lines = [line for line in text.split('\n')]
        buffer_tail = vim.current.buffer[pos:]  # Original end of the file
        new_tail = lines + buffer_tail  # Prepend our data
        del(vim.current.buffer[pos:])  # delete old data
        vim.current.buffer.append(new_tail)  # extend new data

    @staticmethod
    def insert_under_cursor(text):
        """
        Example:
            >>> from vimtk._demo import vimmock
            >>> import ubelt as ub
            >>> vim = vimmock.patch_vim()
            >>> vim.setup_text('foo')
            >>> TextInsertor.insert_under_cursor('bar')
            >>> print(vim.current.buffer._text)
            foo
            bar
        """
        import vim
        (row, col) = vim.current.window.cursor
        # Rows are 1 indexed, so no need to increment
        TextInsertor.insert_at(text, row)

    def insert_over_selection(text):
        import vim
        buf = vim.current.buffer
        # These are probably 1 based
        (row1, col1) = buf.mark('<')
        (row2, col2) = buf.mark('>')
        TextInsertor.insert_between_lines(text, row1, row2)

    def insert_between_lines(text, row1, row2):
        import vim
        buffer_tail = vim.current.buffer[row2:]  # Original end of the file
        lines = [line.encode('utf-8') for line in text.split('\n')]
        new_tail  = lines + buffer_tail
        del(vim.current.buffer[row1 - 1:])  # delete old data
        vim.current.buffer.append(new_tail)  # append new data


class Python(object):
    """
    Tools for handling python-specific functions
    """

    @staticmethod
    def is_module_pythonfile():
        from os.path import splitext
        import vim
        modpath = vim.current.buffer.name
        ext = splitext(modpath)[1]
        ispyfile = ext == '.py'
        logger.debug('is_module_pythonfile?')
        logger.debug('  * modpath = %r' % (modpath,))
        logger.debug('  * ext = %r' % (ext,))
        logger.debug('  * ispyfile = %r' % (ispyfile,))
        return ispyfile

    @staticmethod
    def find_import_row():
        """
        Find lines where import block begins (after __future__)
        """
        in_comment = False
        import vim
        row = 0
        # FIXME: currently heuristic based
        for row, line in enumerate(vim.current.buffer):
            if not in_comment:
                if line.strip().startswith('#'):
                    pass
                elif line.strip().startswith('"""'):
                    in_comment = '"'
                elif line.strip().startswith("''''"):
                    in_comment = "'"
                elif line.startswith('from __future__'):
                    pass
                elif line.startswith('import'):
                    break
                elif line.startswith('from'):
                    break
                else:
                    break
            else:
                if line.strip().endswith(in_comment * 3):
                    in_comment = False
        return row

    @staticmethod
    def prepend_import_block(text):
        import vim
        row = Python.find_import_row()
        # FIXME: doesnt work right when row=0
        buffer_tail = vim.current.buffer[row:]
        lines = [line.encode('utf-8') for line in text.split('\n')]
        lines = [x for x in lines if x]

        logger.info('lines = {!r}'.format(lines))
        new_tail  = lines + buffer_tail
        del(vim.current.buffer[row:])  # delete old data
        # vim's buffer __del__ method seems to not work when the slice is 0:None.
        # It should remove everything, but it seems that one item still exists
        # It seems we can never remove that last item, so we have to hack.
        hackaway_row0 = row == 0 and len(vim.current.buffer) == 1
        # print(len(vim.current.buffer))
        # print('vim.current.buffer = {!r}'.format(vim.current.buffer[:]))
        vim.current.buffer.append(new_tail)  # append new data
        if hackaway_row0:
            del vim.current.buffer[0]


def preprocess_executable_text(text):
    """
    Handles the case where we are trying to docstrings paste into IPython.
    """
    import textwrap
    logger.debug('preprocesing executable text')

    # Prepare to send text to xdotool
    text = textwrap.dedent(text)

    # Preprocess the strings a bit
    lines = text.splitlines(True)

    # Handle C++ pybind11 docs
    if all(re.match(r'" *(>>>)|(\.\.\.) .*', line) for line in lines):
        if all(line.strip().endswith('"') for line in lines):
            new_lines = []
            for line in lines:
                if line.endswith('\\n"\n'):
                    line = line[1:-4] + '\n'
                elif line.endswith('"\n'):
                    line = line[1:-2] + '\n'
                elif line.endswith('\\n"'):
                    line = line[1:-3]
                elif line.endswith('"'):
                    line = line[1:-1]
                else:
                    raise AssertionError('unknown case')
                new_lines.append(line)
            lines = new_lines
            text = textwrap.dedent(''.join(lines))
            lines = text.splitlines(True)

    # Strip docstring prefix
    if all(line.startswith(('>>> ', '...')) for line in lines):
        lines = [line[4:] for line in lines]
        text = ''.join(lines)
    text = textwrap.dedent(text)
    return text


def execute_text_in_terminal(text, return_to_vim=True):
    """
    Execute the current text currently selected **vim** text


    The steps taken:

        (1) Takes a block of text,

        (2) copies it to the clipboard,

        (3) finds the most recently used terminal,

        (4) pastes the text into the most recently used terminal,

        (5) presses enter (if needed),

            * to run what presumably is a command or script,

        (6) and then returns focus to vim.

    TODO:

        * If currently focused on a terminal, then focus in a different
            terminal!

        * User specified terminal pattern

        * User specified paste keypress

        * Allow usage from non-gui terminal vim.
            (ensure we can detect if we are running in a terminal and
             register our window as the active vim, and then paste into
             the second mru terminal)

    """
    logger.debug('execute_text_in_terminal')
    # Copy the text to the clipboard
    Clipboard.copy(text)

    terminal_pattern = CONFIG.get('vimtk_terminal_pattern', None)
    vimtk_multiline_num_press_enter = CONFIG.get('vimtk_multiline_num_press_enter', 3)

    # Build xdtool script
    if sys.platform.startswith('win32'):
        from vimtk import win32_ctrl
        import pywinauto
        active_gvim = win32_ctrl.find_window('gvim.exe')
        # TODO: custom terminal spec
        # Make sure regexes are bash escaped
        if terminal_pattern is None:
            terminal_pattern = '|'.join(map(re.escape, [
                'cmd.exe',
                'Cmder',
            ]))
        terminal = win32_ctrl.find_window(terminal_pattern)
        terminal.focus()
        # TODO: some terminals paste with a right click on win32
        # support these.
        pywinauto.keyboard.SendKeys('^v')
        pywinauto.keyboard.SendKeys('{ENTER}')
        pywinauto.keyboard.SendKeys('{ENTER}')
        if '\n' in text:
            for _ in range(vimtk_multiline_num_press_enter - 2):
                pywinauto.keyboard.SendKeys('{ENTER}')
        if return_to_vim:
            active_gvim.focus()
    else:
        if terminal_pattern is None:
            terminal_pattern = xctrl._wmctrl_terminal_patterns()

        # Sequence of key presses that will trigger a paste event
        paste_keypress = 'ctrl+shift+v'

        if True:
            sleeptime = .01
            import time
            time.sleep(.05)

            xctrl.XCtrl.cmd('xset r off')

            active_gvim = xctrl.XWindow.current()
            xctrl.XWindow.find(terminal_pattern).focus(sleeptime)
            xctrl.XCtrl.send_keys(paste_keypress, sleeptime)
            xctrl.XCtrl.send_keys('KP_Enter', sleeptime)
            if '\n' in text:
                # Press enter multiple times for multiline texts
                for _ in range(vimtk_multiline_num_press_enter - 1):
                    xctrl.XCtrl.send_keys('KP_Enter', sleeptime)
            if return_to_vim:
                active_gvim.focus(sleeptime)

            xctrl.XCtrl.cmd('xset r on')
        else:
            doscript = [
                ('remember_window_id', 'ACTIVE_GVIM'),
                ('focus', terminal_pattern),
                ('key', paste_keypress),
                ('key', 'KP_Enter'),
            ]
            if '\n' in text:
                # Press enter twice for multiline texts
                doscript += [
                    ('key', 'KP_Enter'),
                ]
            if return_to_vim:
                doscript += [
                    ('focus_id', '$ACTIVE_GVIM'),
                ]
            # execute script
            xctrl.XCtrl.do(*doscript, sleeptime=.01)


def vim_argv(defaults=None):
    """
    Helper for parsing vimscript function arguments

    Gets the arguments to the current variable args vim function

    Notes:

        For instance if you have a vim function

        .. code:: vim

            func! foo(...)
                echo "hi"
                python << EOF
                import vimtk
                # You could use this to extract what the args that it was
                # called with were.
                argv = vimtk.vim_argv()
                print('argv = {!r}'.format(argv))
                EOF
            endfunc

    """
    import vim
    nargs = int(vim.eval('a:0'))
    print('nargs = {!r}'.format(nargs))
    argv = [vim.eval('a:{}'.format(i + 1)) for i in range(nargs)]
    if defaults is not None:
        # fill the remaining unspecified args with defaults
        n_remain = len(defaults) - len(argv)
        if n_remain > 0:
            remain = defaults[-n_remain:]
            argv += remain
    return argv


def get_current_fpath():
    """
    Example:
        >>> from vimtk._demo import vimmock
        >>> vim = vimmock.patch_vim()
        >>> vim.setup_text('', 'foo.txt')
        >>> fpath = get_current_fpath()
        >>> assert fpath == 'foo.txt'
    """
    import vim
    fpath = vim.current.buffer.name
    return fpath


def get_current_filetype():
    """
    Example:
        >>> from vimtk._demo import vimmock
        >>> vim = vimmock.patch_vim()
        >>> vim.setup_text('', 'foo.sh')
        >>> filetype = get_current_filetype()
        >>> assert filetype == 'sh'
    """
    import vim
    filetype = vim.eval('&ft')
    return filetype


def ensure_normalmode():
    """
    References:
        http://stackoverflow.com/questions/14013294/vim-how-to-detect-the-mode-in-which-the-user-is-in-for-statusline
    """
    allmodes = {
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
    import vim
    current_mode_code = vim.eval('mode()')
    current_mode = allmodes.get(current_mode_code, current_mode_code)
    if current_mode == 'Normal':
        return
    else:
        logger.debug('current_mode_code = %r' % current_mode)
        logger.debug('current_mode = %r' % current_mode)
    vim.command("ESC")


def autogen_imports(fpath_or_text):
    """
    Generate import statements for python code

    Example:
        >>> import vimtk
        >>> source = ub.codeblock(
            '''
            math
            it
            ''')
        >>> text = vimtk.autogen_imports(source)
        >>> print(text)
        import itertools as it
        import math
    """
    try:
        import xinspect
    except Exception:
        print('UNABLE TO IMPORT XINSPECT')
        print('sys.prefix = {!r}'.format(sys.prefix))
        raise
    from os.path import exists
    from xinspect.autogen import Importables
    importable = Importables()
    importable._use_recommended_defaults()

    base = {
        'it': 'import itertools as it',
        'nh': 'import netharn as nh',
        'np': 'import numpy as np',
        'pd': 'import pandas as pd',
        'ub': 'import ubelt as ub',
        'nx': 'import networkx as nx',
        'Image': 'from PIL import Image',
        'mpl': 'import matplotlib as mpl',
        'nn': 'from torch import nn',
        'torch_data': 'import torch.utils.data as torch_data',
        'F': 'import torch.nn.functional as F',
        'math': 'import math',
    }
    importable.known.update(base)

    user_importable = None
    try:
        user_importable = CONFIG.get('vimtk_auto_importable_modules')
        importable.known.update(user_importable)
    except Exception as ex:
        logger.info('ex = {!r}'.format(ex))
        logger.info('ERROR user_importable = {!r}'.format(user_importable))

    kw = {'importable': importable}
    if exists(fpath_or_text):
        kw['fpath'] = fpath_or_text
    else:
        kw['source'] = fpath_or_text
    lines = xinspect.autogen_imports(**kw)

    x = ub.group_items(lines, [x.startswith('from ') for x in lines])
    ordered_lines = []
    ordered_lines += sorted(x.get(False, []))
    ordered_lines += sorted(x.get(True, []))
    import_block = '\n'.join(ordered_lines)
    return import_block


def is_url(text):
    """ heuristic check if str is url formatted """
    return any([
        text.startswith('http://'),
        text.startswith('https://'),
        text.startswith('www.'),
        '.org/' in text,
        '.com/' in text,
    ])


def extract_url_embeding(word):
    """
    parse several common ways to embed url within a "word"
    """
    # rst url embedding
    if word.startswith('<') and word.endswith('>`_'):
        word = word[1:-3]
    # markdown url embedding
    if word.startswith('[') and word.endswith(')'):
        import parse
        pres = parse.parse('[{tag}]({ref})', word)
        if pres:
            word = pres.named['ref']
    return word


def find_and_open_path(path, mode='split', verbose=0,
                       enable_python=True,
                       enable_url=True, enable_cli=True):
    """
    Fancy-Find. Does some magic to try and find the correct path.

    Currently supports:
        * well-formed absolute and relatiave paths
        * ill-formed relative paths when you are in a descendant directory
        * python modules that exist in the PYTHONPATH

    """
    import os

    def try_open(path):
        # base = '/home/joncrall/code/VIAME/packages/kwiver/sprokit/src/bindings/python/sprokit/pipeline'
        # base = '/home'
        if path and exists(path):
            if verbose:
                print('EXISTS path = {!r}\n'.format(path))
            open_path(path, mode=mode, verbose=verbose)
            return True

    def expand_module(path):
        from xdoctest import static_analysis as static
        try:
            path = path.split('.')[0]
            print('expand path = {!r}'.format(path))
            path = static.modname_to_modpath(path)
            print('expanded path = {!r}'.format(path))
        except Exception as ex:
            print('ex = {!r}'.format(ex))
            return None
        return path

    def expand_module_prefix(path):
        # TODO: we could parse the AST to figure out if the prefix is an
        # alias
        # for a known module.
        from xdoctest import static_analysis as static
        # Check if the path certainly looks like it could be a chain of
        # python
        # attribute accessors.
        if re.match(r'^[\w\d_.]*$', path):
            parts = path.split('.')
            for i in reversed(range(len(parts))):
                prefix = '.'.join(parts[:i])
                path = static.modname_to_modpath(prefix)
                if path is not None:
                    print('expanded prefix = {!r}'.format(path))
                    return path
        print('expanded prefix = {!r}'.format(None))
        return None

    if enable_url:
        # https://github.com/Erotemic
        url = extract_url_embeding(path)
        if is_url(url):
            import webbrowser
            browser = webbrowser.open(url)
            # browser = webbrowser.get('google-chrome')
            browser.open(url)
            # ut.open_url_in_browser(url, 'google-chrome')
            return

    path = expanduser(path)
    if try_open(path):
        return

    if try_open(os.path.expandvars(path)):
        return

    if enable_cli:
        # Strip off the --argname= prefix
        match = re.match(r'--[\w_]*=', path)
        if match:
            path = path[match.end():]

    # path = 'sprokit/pipeline/pipeline.h'
    # base = os.getcwd()
    # base = '/home/joncrall/code/VIAME/packages/kwiver/sprokit/src/bindings/python/sprokit/pipeline'

    if path.startswith('<') and path.endswith('>'):
        path = path[1:-1]
    if path.startswith('`') and path.endswith('`'):
        path = path[1:-1]
    if path.endswith(':'):
        path = path[:-1]
    path = os.path.expandvars(path)
    path = expanduser(path)  # expand again in case a prefix was removed
    if try_open(path):
        return

    def ancestor_paths(start=None, limit={}):
        """
        All paths above you
        """
        limit = {expanduser(p) for p in limit}.union(set(limit))
        if start is None:
            start = os.getcwd()
        path = start
        prev = None
        while path != prev and prev not in limit:
            yield path
            prev = path
            path = os.path.dirname(path)

    def search_candidate_paths(candidate_path_list, candidate_name_list=None,
                               priority_paths=None, required_subpaths=[],
                               verbose=None):
        """
        searches for existing paths that meed a requirement

        Args:
            candidate_path_list (list): list of paths to check. If
                candidate_name_list is specified this is the dpath list instead
            candidate_name_list (list): specifies several names to check
                (default = None)
            priority_paths (None): specifies paths to check first.
                Ignore candidate_name_list (default = None)
            required_subpaths (list): specified required directory structure
                (default = [])
            verbose (bool):  verbosity flag(default = True)

        Returns:
            str: return_path

        CommandLine:
            xdoctest -m utool.util_path --test-search_candidate_paths

        Example:
            >>> # DISABLE_DOCTEST
            >>> from utool.util_path import *  # NOQA
            >>> candidate_path_list = [ub.truepath('~/RPI/code/utool'),
            >>>                        ub.truepath('~/code/utool')]
            >>> candidate_name_list = None
            >>> required_subpaths = []
            >>> verbose = True
            >>> priority_paths = None
            >>> return_path = search_candidate_paths(candidate_path_list,
            >>>                                      candidate_name_list,
            >>>                                      priority_paths, required_subpaths,
            >>>                                      verbose)
            >>> result = ('return_path = %s' % (str(return_path),))
            >>> print(result)
        """
        if verbose is None:
            verbose = 1

        if verbose >= 1:
            print('[search_candidate_paths] Searching for candidate paths')

        if candidate_name_list is not None:
            candidate_path_list_ = [join(dpath, fname) for dpath, fname in
                                    it.product(candidate_path_list,
                                               candidate_name_list)]
        else:
            candidate_path_list_ = candidate_path_list

        if priority_paths is not None:
            candidate_path_list_ = priority_paths + candidate_path_list_

        return_path = None
        for path in candidate_path_list_:
            if path is not None and exists(path):
                if verbose >= 2:
                    print('[search_candidate_paths] Found candidate directory %r' % (path,))
                    print('[search_candidate_paths] ... checking for approprate structure')
                # tomcat directory exists. Make sure it also contains a webapps dir
                subpath_list = [join(path, subpath) for subpath in required_subpaths]
                if all(exists(path_) for path_ in subpath_list):
                    return_path = path
                    if verbose >= 2:
                        print('[search_candidate_paths] Found acceptable path')
                    return return_path
                    break
        if verbose >= 1:
            print('[search_candidate_paths] Failed to find acceptable path')
        return return_path

    # Search downwards for relative paths
    candidates = []
    if not os.path.isabs(path):
        limit = {'~', os.path.expanduser('~')}
        start = os.getcwd()
        candidates += list(ancestor_paths(start, limit=limit))
    candidates += os.environ['PATH'].split(os.sep)
    result = search_candidate_paths(candidates, [path], verbose=verbose)
    if result is not None:
        path = result

    current_fpath = get_current_fpath()
    if os.path.islink(current_fpath):
        newbase = os.path.dirname(os.path.realpath(current_fpath))
        resolved_path = os.path.join(newbase, path)
        if try_open(resolved_path):
            return

    if try_open(path):
        return
    else:
        print('enable_python = {!r}'.format(enable_python))
        if enable_python:
            pypath = expand_module(path)
            print('pypath = {!r}'.format(pypath))
            if try_open(pypath):
                return
            pypath = expand_module_prefix(path)
            print('pypath = {!r}'.format(pypath))
            if try_open(pypath):
                return

        if re.match(r'--\w*=.*', path):
            # try and open if its a command line arg
            stripped_path = expanduser(re.sub(r'--\w*=', '', path))
            if try_open(stripped_path):
                return
        #vim.command('echoerr "Could not find path={}"'.format(path))
        print('Could not find path={!r}'.format(path))


def open_path(fpath, mode='e', nofoldenable=False, verbose=0):
    """
    Execs new splits / tabs / etc

    Weird this wont work with directories (on my machine), see
    [vim_split_issue]_.

    Args:
        fpath : file path to open
        mode: how to open the new file
            (valid options: split, vsplit, tabe, e, new, ...)

    References:
        .. [vim_split_issue] https://superuser.com/questions/1243344/vim-wont-split-open-a-directory-from-python-but-it-works-interactively

    Ignore:
        ~/.bashrc
        ~/code
    """
    import vim
    fpath = expanduser(fpath)
    if not exists(fpath):
        print("FPATH DOES NOT EXIST")
    # command = '{cmd} {fpath}'.format(cmd=cmd, fpath=fpath)
    if isdir(fpath):
        # Hack around directory problem
        if mode.startswith('e'):
            command = ':Explore! {fpath}'.format(fpath=fpath)
        elif mode.startswith('sp'):
            command = ':Hexplore! {fpath}'.format(fpath=fpath)
        elif mode.startswith('vs'):
            command = ':Vexplore! {fpath}'.format(fpath=fpath)
        else:
            raise NotImplementedError('implement fpath cmd for me')
    else:
        command = ":exec ':{mode} {fpath}'".format(mode=mode, fpath=fpath)

    if verbose:
        print('command = {!r}\n'.format(command))

    try:
        vim.command(command)
    except Exception as ex:
        print('FAILED TO OPEN PATH')
        print('ex = {!r}'.format(ex))
        raise
        pass

    if nofoldenable:
        vim.command(":set nofoldenable")


def find_pattern_above_row(pattern, line_list='current', row='current', maxIter=50):
    """
    searches a few lines above the curror until it **matches** a pattern
    """
    import re
    if row == 'current':
        import vim
        row = vim.current.window.cursor[0] - 1
        line_list = vim.current.buffer
    # Iterate until we match.
    # Janky way to find function / class name
    for ix in it.count(0):
        pos = row - ix
        if maxIter is not None and ix > maxIter:
            break
        if pos < 0:
            break
        searchline = line_list[pos]
        if re.match(pattern, searchline) is not None:
            return searchline, pos
    return None


def get_first_nonempty_line_after_cursor():
    import vim
    buf = vim.current.buffer
    (row, col) = vim.current.window.cursor
    for i in range(len(buf) - row):
        line = buf[row + i]
        if line:
            return line


def get_indentation(line_):
    """
    returns the number of preceding spaces
    """
    return len(line_) - len(line_.lstrip())


def get_minimum_indentation(text):
    r"""
    returns the number of preceding spaces

    Args:
        text (str): unicode text

    Returns:
        int: indentation

    Example:
        >>> text = '    foo\n   bar'
        >>> result = get_minimum_indentation(text)
        >>> print(result)
        3
    """
    lines = text.split('\n')
    indentations = [get_indentation(line_)
                    for line_ in lines  if len(line_.strip()) > 0]
    if len(indentations) == 0:
        return 0
    return min(indentations)


def _linux_install():
    """
    Installs vimtk to the standard pathogen bundle directory
    """
    import pkg_resources  # NOQA
    import vimtk  # NOQA
    # TODO: finishme
    # vim_data = pkg_resources.resource_string(vimtk.__name__, "vim")


CONFIG = Config()

if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/code/vimtk/autoload
        python ~/code/vimtk/autoload/vimtk.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
