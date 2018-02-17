import re
import sys
import ubelt as ub  # NOQA
from vimtk import clipboard
from vimtk import xctrl


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
    # Copy the text to the clipboard
    clipboard.copy(text)

    # Build xdtool script
    if sys.platform.startswith('win32'):
        print('win32 cannot copy to terminal yet. Just copied to clipboard. '
              ' Needs AHK support for motion?')
        return

    def _wmctrl_terminal_pattern():
        # Make sure regexes are bash escaped
        terminal_pattern = CONFIG.get('vimtk_terminal_pattern', None)
        if terminal_pattern is None:
            terminal_pattern = r'\|'.join([
                'terminal',
                re.escape('terminator.Terminator'),  # gtk3 terminator
                re.escape('x-terminal-emulator.X-terminal-emulator'),  # gtk2 terminator
                # other common terminal applications
                'tilix',
                'konsole',
                'rxvt',
                'terminology',
                'xterm',
                'tilda',
                'Yakuake',
            ])
            return terminal_pattern

    terminal_pattern = _wmctrl_terminal_pattern()

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


CONFIG = Config()

if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/code/vimtk/autoload
        python ~/code/vimtk/autoload/vimtk.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
