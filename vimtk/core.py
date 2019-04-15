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
# logger.basicConfig()
logger.setLevel(logging.INFO)


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
    """
    Tools for selecting and reading text from Vim
    """

    @staticmethod
    def word_at_cursor(url_ok=False):
        """ returns the word highlighted by the curor """
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
        """ make sure the vim function calling this has a range after ()

        Currently used by <ctrl+g>

        References:
            http://stackoverflow.com/questions/18165973/vim-obtain-string-between-visual-selection-range-with-python

        SeeAlso:
            ~/local/vim/rc/custom_misc_functions.vim

        Test paragraph.
        Far out in the uncharted backwaters of the unfashionable end of the western
        spiral arm of the Galaxy lies a small unregarded yellow sun. Orbiting this at a
        distance of roughly ninety-two million miles is an utterly insignificant little
        blue green planet whose ape-descended life forms are so amazingly primitive
        that they still think digital watches are a pretty neat idea.
        % ---
        one. two three. four.

        """
        import vim
        logger.debug('grabbing visually selected text')
        buf = vim.current.buffer
        (lnum1, col1) = buf.mark('<')
        (lnum2, col2) = buf.mark('>')
        text = TextSelector.text_between_lines(lnum1, lnum2, col1, col2)
        return text

    @staticmethod
    def text_between_lines(lnum1, lnum2, col1=0, col2=sys.maxsize - 1):
        import vim
        lines = vim.eval('getline({}, {})'.format(lnum1, lnum2))
        lines = [ub.ensure_unicode(line) for line in lines]
        try:
            if len(lines) == 0:
                pass
            elif len(lines) == 1:
                lines[0] = lines[0][col1:col2 + 1]
            else:
                lines[0] = lines[0][col1:]
                lines[-1] = lines[-1][:col2 + 1]
            text = '\n'.join(lines)
        except Exception:
            print(ub.repr2(lines))
            raise
        return text

    @staticmethod
    def line_at_cursor():
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
    if all(re.match('" *(>>>)|(\.\.\.) .*', line) for line in lines):
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
    """
    import vim
    nargs = int(vim.eval('a:0'))
    argv = [vim.eval('a:{}'.format(i + 1)) for i in range(nargs)]
    if defaults is not None:
        # fill the remaining unspecified args with defaults
        n_remain = len(defaults) - len(argv)
        remain = defaults[-n_remain:]
        argv += remain
    return argv


def get_current_fpath():
    import vim
    fpath = vim.current.buffer.name
    return fpath


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
    #vim.command("ESC")


def autogen_imports(fpath_or_text):
    """
    Generate import statements for python code

    Example:
        >>> import vimtk
        >>> source = ub.codeblock(
            '''
            numpy
            ub
            nh
            ''')
        >>> text = vimtk.autogen_imports(source)
        >>> print(text)
        import netharn as nh
        import numpy
        import ubelt as ub
    """
    import xinspect
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
        # 'Variable': 'from torch.autograd import Variable',
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


def _linux_install():
    """
    Installs vimtk to the standard pathogen bundle directory
    """
    import pkg_resources
    import vimtk
    # TODO: finishme
    vim_data = pkg_resources.resource_string(vimtk.__name__, "vim")


CONFIG = Config()

if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/code/vimtk/autoload
        python ~/code/vimtk/autoload/vimtk.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
