import re
import sys
import ubelt as ub  # NOQA
from vimtk import xctrl
from vimtk import cplat
import logging

logger = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        self.default = {
            'vimtk_terminal_pattern': None,
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
            line (?):
            col (?):

        CommandLine:
            python  ~/local/vim/rc/pyvim_funcs.py --test-get_word_in_line_at_col

        Example:
            >>> # DISABLE_DOCTEST
            >>> from pyvim_funcs import *  # NOQA
            >>> line = 'myvar.foo = yourvar.foobar'
            >>> line = 'def loadfunc(self):'
            >>> col = 6
            >>> nonword_chars=' \t\n\r[](){}:;.,"\'\\/'
            >>> word = get_word_in_line_at_col(line, col, nonword_chars)
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
        logger.debug('grabbing visually selected text')
        import vim
        buf = vim.current.buffer
        (lnum1, col1) = buf.mark('<')
        (lnum2, col2) = buf.mark('>')
        text = TextSelector.text_between_lines(lnum1, lnum2, col1, col2)
        return text

    @staticmethod
    def text_between_lines(lnum1, lnum2, col1=0, col2=sys.maxsize - 1):
        import vim
        lines = vim.eval('getline({}, {})'.format(lnum1, lnum2))
        import utool as ut
        lines = ut.ensure_unicode_strlist(lines)
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
            import utool as ut
            ut.ENABLE_COLORS = False
            ut.util_str.ENABLE_COLORS = False
            ut.util_dbg.COLORED_EXCEPTIONS = False
            print(ut.repr2(lines))
            raise
        return text

    @staticmethod
    def line_at_cursor():
        logger.debug('grabbing text at current line')
        import vim
        buf = vim.current.buffer
        (row, col) = vim.current.window.cursor
        line = buf[row - 1]
        return line


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
    Takes a block of text, copies it to the clipboard, pastes it into the most
    recently used terminal, presses enter (if needed) to run what presumably is
    a command or script, and then returns to vim.

    TODO:
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

    # Build xdtool script
    if sys.platform.startswith('win32'):
        from vimtk import win32_ctrl
        import pywinauto
        active_gvim = win32_ctrl.find_window('gvim.exe')
        terminal = win32_ctrl.find_window('cmd.exe')
        terminal.focus()
        pywinauto.keyboard.SendKeys('^v')
        pywinauto.keyboard.SendKeys('{ENTER}')
        pywinauto.keyboard.SendKeys('{ENTER}')
        active_gvim.focus()
        return

    # Make sure regexes are bash escaped
    terminal_pattern = CONFIG.get('vimtk_terminal_pattern', None)
    if terminal_pattern is None:
        terminal_pattern = xctrl._wmctrl_terminal_patterns()

    # Sequence of key presses that will trigger a paste event
    paste_keypress = 'ctrl+shift+v'

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


def is_module_pythonfile():
    from os.path import splitext
    import vim
    modpath = vim.current.buffer.name
    ext = splitext(modpath)[1]
    ispyfile = ext == '.py'
    logging.debug('is_module_pythonfile?')
    logging.debug('  * modpath = %r' % (modpath,))
    logging.debug('  * ext = %r' % (ext,))
    logging.debug('  * ispyfile = %r' % (ispyfile,))
    return ispyfile


def get_current_fpath():
    import vim
    fpath = vim.current.buffer.name
    return fpath


CONFIG = Config()

if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/code/vimtk/autoload
        python ~/code/vimtk/autoload/vimtk.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
