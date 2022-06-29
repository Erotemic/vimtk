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


def mockvim(fpath=None, text=None):
    """
    Setup a dummy "vim" module with a specific buffer

    Useful for prototyping new commands and testing

    Args:
        fpath (PathLike | None):
            File to mock open. Will read the text if it exists.

        text (str | None):
            text of the mock buffer. If none, tries to read from the file path.

    Returns:
        vimtk._demo.vimmock.mocked.VimMock:
            the mock vim module

    Example:
        >>> import vimtk
        >>> vim = vimtk.mockvim()
        >>> # The mock mirrors the vim module as best as it can
        >>> print('vim.current.buffer = {}'.format(vim.current.buffer))
        >>> print('vim.current.buffer.name = {}'.format(vim.current.buffer.name))
        >>> vim.eval("let g:custom_global = 'custom_val'")
        >>> value = vim.eval('get(g:, "custom_global")')
        >>> assert value == 'custom_val'
    """
    import os
    from vimtk._demo import vimmock
    vim = vimmock.patch_vim()
    if text is not None:
        if fpath is None:
            fpath = ''
        vim.setup_text(text, name=os.fspath(fpath))
    elif fpath is not None:
        vim.open_file(fpath)
    return vim


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

    Notes:
        >>> import vimtk
        >>> vim = vimtk.mockvim()
        >>> vim.eval("let g:vimtk_sys_path = ['$HOME/code/netharn']")
        >>> vimtk.CONFIG.get('vimtk_sys_path')
        >>> vimtk.CONFIG['vimtk_auto_importable_modules']
        >>> # Should the vim variable override or update the default config?
        >>> vim.eval("let g:vimtk_auto_importable_modules = {'spam': 'import spam'}")
        >>> vimtk.CONFIG['vimtk_auto_importable_modules']
    """
    def __init__(self):
        # TODO: use scriptconfig to add helps?
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
            },

            # Additional paths to search when resolving python modnames
            'vimtk_sys_path': [],
        }
        self.state = self.default.copy()
        pass

    def __getitem__(self, key):
        value = self.get(key, default=self.state[key])
        return value

    def __setitem__(self, key, value):
        self.state[key] = value

    def get(self, key, default=None, context='g'):
        """ gets the value of a vim variable and defaults if it does not exist """
        import vim
        assert key in self.default
        varname = '{}:{}'.format(context, key)
        var_exists = int(vim.eval('exists("{}")'.format(varname)))
        if var_exists:
            value = vim.eval('get({}:, "{}")'.format(context, key))
            # Hack: for dictionaries, update instead of overriding?
            # Not sure if this is a good idea
            if isinstance(value, dict):
                value = ub.dict_union(default, value)
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
    def current_indent(url_ok=False):
        """
        Returns the indentation that should be used when inserting new lines.

        Example:
            >>> import vimtk
            >>> import ubelt as ub
            >>> import vimtk
            >>> vim = vimtk.mockvim(text=ub.codeblock(
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
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim()
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
            >>> import vimtk
            >>> line = 'myvar.foo = yourvar.foobar'
            >>> line = 'def loadfunc(self):'
            >>> col = 6
            >>> nonword_chars=' \t\n\r[](){}:;.,"\'\\/'
            >>> word = vimtk.TextSelector.get_word_in_line_at_col(line, col, nonword_chars)
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
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim()
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
        """
        """
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
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim()
            >>> vim.setup_text(ub.codeblock(
            >>>     '''
            >>>     def foo():
            >>>         return 1
            >>>     def bar():
            >>>         return 2
            >>>     '''))
            >>> vim.move_cursor(3)
            >>> line = vimtk.TextSelector.line_at_cursor()
            >>> assert line == 'def bar():'
        """
        import vim
        logger.debug('grabbing text at current line')
        buf = vim.current.buffer
        (row, col) = vim.current.window.cursor
        line = buf[row - 1]
        return line

    @staticmethod
    def paragraph_range_at_cursor():
        r"""
        Get the start and end lines for a paragraph at the cursor

        Example:
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim()
            >>> text = ub.codeblock(
                    '''
                    par1 par1 par1
                      par1 par1
                    par1 par1

                    par2

                    par3 par3
                         par3
                    ''')
            >>> vim.setup_text(text)
            >>> ranges = []
            >>> for lineno in range(1, text.count(chr(10)) + 1):
            >>>     vim.move_cursor(lineno)
            >>>     par_range = vimtk.TextSelector.paragraph_range_at_cursor()
            >>>     ranges.append(par_range)
            >>> print('ranges = {}'.format(ub.repr2(ranges, nl=0)))
            ranges = [(0, 3), (0, 3), (0, 3), (4, 4), (5, 5), (6, 6), (7, 7)]
        """
        import vim
        import ubelt as ub
        logger.debug('grabbing text at current line')

        def is_paragraph_end(line_):
            # Hack, par_marker_list should be an argument
            striped_line = ub.ensure_unicode(line_.strip())
            isblank = striped_line == ''
            if isblank:
                return True
            # TODO: fixme, move to some configuration file
            par_marker_list = [
                #'\\noindent',
                '\\begin{equation}',
                '\\end{equation}',
                '% ---',
            ]
            return any(striped_line.startswith(marker)
                       for marker in par_marker_list)

        def find_paragraph_end(row_, direction=1):
            """
            returns the line that a paragraph ends on in some direction
            """
            # TODO: validate logic.
            line_list = vim.current.buffer
            line_ = line_list[row_ - 1]
            if (row_ == 0 or row_ == len(line_list) - 1):
                return row_
            if is_paragraph_end(line_):
                return row_
            while True:
                if (row_ == -1 or row_ == len(line_list)):
                    break
                line_ = line_list[row_ - 1]
                if is_paragraph_end(line_):
                    break
                row_ += direction
            row_ -= direction
            return row_

        (row, col) = vim.current.window.cursor
        row1 = find_paragraph_end(row, -1)
        row2 = find_paragraph_end(row, +1)
        # row1 = max(1, row1)
        par_range = (row1, row2)
        return par_range


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
        # This is 1 indexed, should we change that?
        (row, col) = vim.current.window.cursor
        return row, col


class TextInsertor(object):
    """
    Tools for inserting text at various positions
    """

    def overwrite(text):
        """
        Overwrites all existing text in the current buffer with new text

        Example:
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim(text='foo')
            >>> vimtk.TextInsertor.overwrite('bar')
            >>> print(vim.current.buffer._text)
        """
        import vim
        lines = text.split('\n')
        vim.current.buffer[:] = lines
        # del (vim.current.buffer[:])
        # vim.current.buffer.append(lines)

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
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim(text='foo')
            >>> vimtk.TextInsertor.insert_under_cursor('bar')
            >>> print(vim.current.buffer._text)
            foo
            bar
        """
        import vim
        (row, col) = vim.current.window.cursor
        # Rows are 1 indexed, so no need to increment
        TextInsertor.insert_at(text, row)

    @staticmethod
    def insert_above_cursor(text):
        """
        Example:
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim()
            >>> vim.setup_text('foo')
            >>> vimtk.TextInsertor.insert_above_cursor('bar')
            >>> print(vim.current.buffer._text)
            bar
            foo
        """
        import vim
        (row, col) = vim.current.window.cursor
        row = row - 1
        TextInsertor.insert_at(text, row)

    @staticmethod
    def insert_over_selection(text):
        import vim
        buf = vim.current.buffer
        # These are probably 1 based
        (row1, col1) = buf.mark('<')
        (row2, col2) = buf.mark('>')
        TextInsertor.insert_between_lines(text, row1, row2)

    @staticmethod
    def insert_between_lines(text, row1, row2):
        import vim
        # print(f'text={text}')
        # print(f'Insert between {row1} {row2}')
        buffer_head = vim.current.buffer[:row1 - 1]  # Original start of the file
        buffer_tail = vim.current.buffer[row2:]  # Original end of the file
        # print(f'buffer_tail={buffer_tail}')
        lines = [line.encode('utf-8') for line in text.split('\n')]
        new_buffer = buffer_head + lines + buffer_tail
        vim.current.buffer[:] = new_buffer
        # del vim.current.buffer[row1 - 1:]  # delete old data
        # vim.current.buffer.append(new_tail)  # append new data


class Mode(object):
    """
    Helper for checking / switching modes
    """
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

    @staticmethod
    def current():
        """
        Return the current mode

        References:
            http://stackoverflow.com/questions/14013294/vim-how-to-detect-the-mode-in-which-the-user-is-in-for-statusline

        Example:
            >>> import vimtk
            >>> vim = vimtk.mockvim()
            >>> vimtk.Mode.current()
            Normal
        """
        import vim
        current_mode_code = vim.eval('mode()')
        current_mode = Mode.vim_mode_codes.get(current_mode_code, current_mode_code)
        return current_mode

    @staticmethod
    def ensure_normal():
        """
        Switch to normal mode

        Example:
            >>> import vimtk
            >>> vim = vimtk.mockvim()
            >>> vimtk.Mode.ensure_normal()
            >>> vimtk.Mode.current()
            Normal
        """
        current_mode = Mode.current()
        import vim
        if current_mode == 'Normal':
            return
        else:
            logger.debug('current_mode_code = %r' % current_mode)
            logger.debug('current_mode = %r' % current_mode)
        vim.command("ESC")


class Python(object):
    """
    Tools for handling python-specific functions
    """

    @staticmethod
    def current_module_info():
        """
        Returns information about current module

        Example:
            >>> import vimtk
            >>> import ubelt as ub
            >>> vim = vimtk.mockvim('foo.py', '')
            >>> info = vimtk.Python.current_module_info()
            >>> print(ub.repr2(info))
        """
        import ubelt as ub
        import vim

        modpath = vim.current.buffer.name
        modname = ub.modpath_to_modname(modpath, check=False)
        moddir, rel_modpath = ub.split_modpath(modpath, check=False)

        from ubelt.util_import import is_modname_importable
        importable = is_modname_importable(modname, exclude=['.'])
        info = {
            'modname': modname,
            'modpath': modpath,
            'importable': importable,
        }
        return info

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

    @staticmethod
    def format_text_as_docstr(text):
        r"""
        CommandLine:
            python  ~/local/vim/rc/pyvim_funcs.py  --test-format_text_as_docstr

        Example:
            >>> import vimtk
            >>> text = ub.codeblock(
                '''
                a = 1
                b = 2
                ''')
            >>> formated_text = vimtk.Python.format_text_as_docstr(text)
            >>> unformated_text = vimtk.Python.unformat_text_as_docstr(formated_text)
            >>> print(formated_text)
            >>> print(unformated_text)
        """
        min_indent = get_minimum_indentation(text)
        indent_ =  ' ' * min_indent
        formated_text = re.sub('^' + indent_, '' + indent_ + '>>> ', text,
                               flags=re.MULTILINE)
        formated_text = re.sub('^$', '' + indent_ + '>>> #', formated_text,
                               flags=re.MULTILINE)
        return formated_text

    @staticmethod
    def unformat_text_as_docstr(formated_text):
        min_indent = get_minimum_indentation(formated_text)
        indent_ =  ' ' * min_indent
        unformated_text = re.sub('^' + indent_ + '>>> ', '' + indent_,
                                 formated_text, flags=re.MULTILINE)
        return unformated_text

    @staticmethod
    def find_func_above_row(row='current', maxIter=50):
        """
        Example:
            >>> import ubelt as ub
            >>> import vimtk
            >>> vim = vimtk.mockvim()
            >>> vim.setup_text(ub.codeblock(
            >>>     '''
            >>>     class Foo:
            >>>         def __init__(self):
            >>>             self.foo = 1
            >>>             self.foo = 2
            >>>     def foo():
            >>>         pass
            >>>     def bar():
            >>>         pass
            >>>     def baz():
            >>>         pass
            >>>     '''))
            >>> vim.move_cursor(8)
            >>> info = vimtk.Python.find_func_above_row()
            >>> print(ub.repr2(info))
            >>> vim.move_cursor(4)
            >>> info = vimtk.Python.find_func_above_row()
            >>> print(ub.repr2(info))
        """
        pattern = r' *(def|class) *(?P<callname>[A-Za-z0-0_]*)\('
        result = find_pattern_above_row(pattern, maxIter=maxIter)
        print('result = {!r}'.format(result))
        if result is not None:
            line, pos = result
            match = re.match(pattern, line)
            callname = match.groupdict()['callname']
        else:
            line = None
            pos = None
            callname = None
        info = {
            'callname': callname,
            'pos': pos,
            'line': line,
        }
        return info

    @staticmethod
    def _convert_dicts_to_literals(text):
        """
        TODO: where does this belong? This is a Python reformater of sorts.

        Example:
            import ubelt as ub
            import vimtk
            vim = text=ub.codeblock(
                '''
                data = dict(
                    key1=12321321,
                    key2='24324324',
                    key3=myfunc(),
                    key4=[
                       1, 2, 3, 4, dict(a='b'),
                    ]
                )
                ''')
            new_text = vimtk.Python._convert_dicts_to_literals(text)
            print(new_text)
        """
        # TODO: probably want a CST transformer instead
        import ast
        import astunparse
        class RewriteDictAsLiteral(ast.NodeTransformer):
            def visit_Call(self, node):
                if node.func.id == 'dict':
                    keys = [ast.Constant(kw.arg) for kw in node.keywords]
                    values = [kw.value for kw in node.keywords]
                    literal = ast.Dict(keys=keys, values=values)
                    return self.visit(literal)

        lvl = get_minimum_indentation(text)
        orig_ptree = ast.parse(ub.codeblock(text))
        xform_ptree = RewriteDictAsLiteral().visit(orig_ptree)
        xform_text = astunparse.unparse(xform_ptree)

        import black
        xform_text = black.format_str(
            xform_text, mode=black.Mode(string_normalization=False)
        )
        new_text = ub.indent(xform_text, ' ' * lvl)
        return new_text

    @staticmethod
    def _convert_selection_to_literal_dict():
        """
        Changes the visual selection from a programatic dictionary to a
        dictionary literal if possible.

        Ignore:
            import ubelt as ub
            import vimtk
            vim = vimtk.mockvim(text=ub.codeblock(
                '''
                data = dict(
                    key1=12321321,
                    key2='24324324',
                    key3=myfunc(),
                    key4=[
                       1, 2, 3, 4, dict(a='b'),
                    ]
                )
                '''))
            vim.current.buffer._visual_select(1, 9)
            vimtk.Python._convert_selection_to_literal_dict()
            print(vimtk.TextSelector.selected_text())
        """
        import vimtk
        text = vimtk.TextSelector.selected_text()
        new_text = vimtk.Python._convert_dicts_to_literals(text)
        vimtk.TextInsertor.insert_over_selection(new_text)


def sys_executable():
    """
    Find the system executable. For whatever reason, vim messes with it.

    References:
        https://github.com/ycm-core/YouCompleteMe/blob/ba7a9f07a57c657c684edb5dde1f1f1dda1c0c7a/python/ycm/paths.py
        https://github.com/davidhalter/jedi-vim/issues/870
    """
    if sys.platform.startswith('win32'):
        executable = join(sys.exec_prefix, 'python.exe')
    else:
        import os
        bin_dpath = join(sys.exec_prefix, 'bin')
        assert exists(bin_dpath)
        pyexe_re = re.compile(r'python([23](\.[5-9])?)?(.exe)?$', re.IGNORECASE )
        candiates = os.listdir(bin_dpath)
        found = []
        for cand in candiates:
            if pyexe_re.match(cand):
                fpath = join(bin_dpath, cand)
                if os.path.isfile(fpath):
                    if os.access(fpath, os.X_OK):
                        found.append(fpath)
        assert len(found) > 0
        executable = found[0]
    return executable


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

    # Currently linux and windows are handled separately. It would be nice to
    # unify them if possible.
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
        if hasattr(pywinauto.keyboard, 'send_keys'):
            send_keys = pywinauto.keyboard.send_keys
        else:
            send_keys = pywinauto.keyboard.SendKeys
        send_keys('^v')
        send_keys('{ENTER}')
        send_keys('{ENTER}')
        if '\n' in text:
            for _ in range(vimtk_multiline_num_press_enter - 2):
                send_keys('{ENTER}')
        if return_to_vim:
            active_gvim.focus()
    else:
        if terminal_pattern is None:
            terminal_pattern = xctrl._wmctrl_terminal_patterns()
        # print('terminal_pattern = {!r}'.format(terminal_pattern))

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

    Example:
        >>> import vimtk
        >>> vim = vimtk.mockvim()
        >>> vim._push_function_stack(name='foo', positional=['val1', 'val2'])
        >>> argv = vimtk.vim_argv()
        >>> assert argv == ['val1', 'val2']
        >>> argv = vimtk.vim_argv(defaults=['a', 'b', 'c'])
        >>> assert argv == ['val1', 'val2', 'c']
        >>> _ = vim._function_stack.pop()
    """
    import vim
    nargs = int(vim.eval('a:0'))
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
        >>> import vimtk
        >>> vim = vimtk.mockvim(fpath='foo.txt', text='')
        >>> fpath = vimtk.get_current_fpath()
        >>> assert fpath == 'foo.txt'
    """
    import vim
    fpath = vim.current.buffer.name
    return fpath


def get_current_filetype():
    """
    Example:
        >>> import vimtk
        >>> vim = vimtk.mockvim(fpath='foo.sh', text='')
        >>> filetype = vimtk.get_current_filetype()
        >>> assert filetype == 'sh'
    """
    import vim
    filetype = vim.eval('&ft')
    return filetype


def ensure_normalmode():
    """
    TODO: Deprecated in favor or Mode.ensure_normal()

    References:
        http://stackoverflow.com/questions/14013294/vim-how-to-detect-the-mode-in-which-the-user-is-in-for-statusline
    """
    return Mode.ensure_normal()


def autogen_imports(fpath_or_text):
    """
    Generate import statements for python code

    Example:
        >>> # xdoctest: +SKIP
        >>> # This test is broken on the windows CI and I dont understand why
        >>> import vimtk
        >>> source = ub.codeblock(
            '''
            math
            it
            ''')
        >>> text = vimtk.autogen_imports(source)
        ...
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
    user_importable = None
    try:
        user_importable = CONFIG['vimtk_auto_importable_modules']
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
    if word.startswith('(') and word.endswith(')'):
        word = word[1:-1]
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
        # TODO: use ubelt util_import instead
        import ubelt as ub
        _debug = 0
        if _debug:
            import sys
            print('sys.base_exec_prefix = {!r}'.format(sys.base_exec_prefix))
            print('sys.base_prefix = {!r}'.format(sys.base_prefix))
            print('sys.exec_prefix = {!r}'.format(sys.exec_prefix))
            print('sys.executable = {!r}'.format(sys.executable))
            print('sys.implementation = {!r}'.format(sys.implementation))
            print('sys.prefix = {!r}'.format(sys.prefix))
            print('sys.version = {!r}'.format(sys.version))
            print('sys.path = {!r}'.format(sys.path))

        import sys
        extra_path = CONFIG.get('vimtk_sys_path')
        sys_path = sys.path + [ub.expandpath(p) for p in extra_path]
        print('expand path = {!r}'.format(path))
        modparts = path.split('.')
        for i in reversed(range(1, len(modparts) + 1)):
            candidate = '.'.join(modparts[0:i])
            print('candidate = {!r}'.format(candidate))
            path = ub.modname_to_modpath(candidate, sys_path=sys_path)
            if path is not None:
                break
        print('expanded modname-to-path = {!r}'.format(path))
        return path

    def expand_module_prefix(path):
        # TODO: we could parse the AST to figure out if the prefix is an alias
        # for a known module.
        # Check if the path certainly looks like it could be a chain of python
        # attribute accessors.
        if re.match(r'^[\w\d_.]*$', path):
            extra_path = CONFIG.get('vimtk_sys_path')
            sys_path = sys.path + [ub.expandpath(p) for p in extra_path]
            parts = path.split('.')
            for i in reversed(range(len(parts))):
                prefix = '.'.join(parts[:i])
                path = ub.modname_to_modpath(prefix, sys_path=sys_path)
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

    TODO: move to some class? Perhaps somethig like Finder?
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
