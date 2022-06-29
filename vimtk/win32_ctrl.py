"""
https://pywinauto.github.io/docs/code/pywinauto.findwindows.html
"""
import ubelt as ub
import logging
import psutil
logger = logging.getLogger(__name__)

# logging.basicConfig()
# logger.setLevel(logging.DEBUG)
# logging.getLogger('parso').setLevel(logging.INFO)


if ub.WIN32:
    import win32gui
    import win32process
    # import win32api
    import win32con
    import ctypes


class Win32Window(ub.NiceRepr):
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __nice__(self):
        fname = self.process_name()
        return str(self.hwnd) + ' ' + fname + ' ' + repr(self.title())

    def title(self):
        """ text in the title bar """
        return win32gui.GetWindowText(self.hwnd)

    def process_id(self):
        thread_id, pid = win32process.GetWindowThreadProcessId(self.hwnd)
        return pid

    def visible(self):
        """
        Returns true if the window is visible (being minimized counts as
        being visible, so this means just ignore all invisible windows for
        our purposes)
        """
        return ctypes.windll.user32.IsWindowVisible(self.hwnd)

    # def process_handle(self):
    #     # https://mail.python.org/pipermail/python-win32/2005-February/002943.html
    #     pid = self.process_id()
    #     print('pid = {!r}'.format(pid))
    #     proc_handle = win32api.OpenProcess(
    #             win32con.PROCESS_ALL_ACCESS, False, pid)
    #     return proc_handle

    def process(self):
        pid = self.process_id()
        proc = psutil.Process(pid)
        return proc
        # exe_fpath = win32process.GetModuleFileNameEx(proc_handle, 0)
        # return exe_fpath

    def process_name(self):
        proc = self.process()
        return proc.name()

    def info(self):
        return {
            'hwnd': self.hwnd,
            # 'proc_handle': self.process_handle(),
            'proc_name': self.process_name(),
            'title': self.title(),
        }

    def focus(self):
        """
        CommandLine:
            python -m vimtk.win32_ctrl Win32Window.focus:0

        Example:
            >>> # xdoc: +REQUIRES(win32)
            >>> # xdoc: +REQUIRES(--has-display)
            >>> win = find_window('gvim.exe')
            >>> win.focus()
        """
        win32gui.SetForegroundWindow(self.hwnd)


# def paste_text_into_terminal():
#     """
#     CommandLine:
#         python -m vimtk.win32_ctrl paste_text_into_terminal

#     Example:
#         >>> paste_text_into_terminal()
#     """
#     import pywinauto
#     terminal = find_window('cmd.exe')
#     terminal.focus()
#     pywinauto.keyboard.SendKeys('^v')
#     pywinauto.keyboard.SendKeys('{ENTER}')

#     from pywinauto.application import Application
#     app = Application()
#     app.Connect(handle=terminal.hwnd)
# logging.getLogger('parso').setLevel(logging.INFO)
#     app.MainWindow.Edit.TypeKeys(r'^v')


def send_keys(keys):
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('keys to send to active window...')


def find_window(proc=None, title=None, visible=True):
    """
    CommandLine:
        python -m vimtk.win32_ctrl find_window

    Example:
        >>> # xdoc: +REQUIRES(win32)
        >>> # xdoc: +REQUIRES(--has-display)
        >>> from vimtk.win32_ctrl import *  # NOQA
        >>> win = find_window('gvim.exe')
        >>> print(win.info())
        >>> win = find_window('cmd.exe')
        >>> print(win.info())
    """
    for win in find_windows(proc, title):
        return win
    raise Exception('Cannot find window matching proc={}, title={}'.format(proc, title))


def find_windows(proc=None, title=None, visible=True):
    """
    CommandLine:
        python -m vimtk.win32_ctrl find_windows

    Example:
        >>> # xdoc: +REQUIRES(win32)
        >>> # xdoc: +REQUIRES(--has-display)
        >>> from vimtk.win32_ctrl import *  # NOQA
        >>> for win in find_windows('gvim.exe'):
        >>>     print(ub.repr2(win.info()))
        >>> for win in find_windows('cmd.exe'):
        >>>     print(ub.repr2(win.info()))
    """
    import re
    flags = re.IGNORECASE
    for win in windows_in_order():
        flag = True
        if proc:
            flag &= bool(re.match(proc, win.process_name(), flags=flags))
        if title:
            flag &= bool(re.match(title, win.title(), flags=flags))
        if visible:
            flag &= win.visible()
        if flag:
            yield win


def current_window_name():
    r"""
    CommandLine:
        python -m vimtk.win32_ctrl current_window_name

    Example:
        >>> # xdoc: +REQUIRES(win32)
        >>> # xdoc: +REQUIRES(--has-display)
        >>> from vimtk.win32_ctrl import *  # NOQA
        >>> result = current_window_name()
        >>> print(result)
    """
    logging.debug('Get current window name')
    hwnd = win32gui.GetForegroundWindow()
    value = Win32Window(hwnd).title()
    logging.debug('... current window name = {!r}'.format(value))
    return value


def windows_in_order():
    """
    Returns windows in z-order (top first)

    References:
        https://stackoverflow.com/questions/6381198/

    CommandLine:
        python -m vimtk.win32_ctrl windows_in_order

    Example:
        >>> # xdoc: +REQUIRES(win32)
        >>> # xdoc: +REQUIRES(--has-display)
        >>> from vimtk.win32_ctrl import *  # NOQA
        >>> result = list(windows_in_order())
        >>> for win in result:
        ...     if win.visible():
        ...         print(win)
    """
    user32 = ctypes.windll.user32
    hwnd = user32.GetTopWindow(None)
    while hwnd:
        win = Win32Window(hwnd)
        yield win
        hwnd = user32.GetWindow(hwnd, win32con.GW_HWNDNEXT)


def findall_window_ids():
    """
    CommandLine:
        python -m vimtk.win32_ctrl findall_window_ids

    Example:
        >>> # xdoc: +REQUIRES(win32)
        >>> # xdoc: +REQUIRES(--has-display)
        >>> from vimtk.win32_ctrl import *  # NOQA
        >>> result = findall_window_ids()
        >>> print(result)
    """
    import pywinauto
    pywinauto.findwindows.enum_windows()
    for hwnd in pywinauto.findwindows.enum_windows():
        win = Win32Window(hwnd)
        if win.visible():
            print(win.info())


# pywinauto.element_info.ElementInfo(    pywinauto.findwindows.enum_windows()[0])
if __name__ == '__main__':
    r"""
    CommandLine:
        python -m vimtk.win32_ctrl
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
