# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ubelt as ub
import sys
import logging
logger = logging.getLogger(__name__)


try:
    import pyperclip
except (ImportError, Exception) as ex:
    msg = ('Python cannot import pyperclip: '
           'python version={}, prefix={}, ex={!r}').format(
               sys.version_info, sys.prefix, ex)
    logger.warn(msg)
    pyperclip = None
    # raise

__PyQt__ = None


class _PyQtWraper(object):
    """
    Lazy import of PyQt 4 or 5

    CommandLine:
        python -m vimtk.cplat _PyQtWraper

    Example:
        >>> # xdoctest: +REQUIRES(module:PyQt5)
        >>> PyQt = import_pyqt()
        >>> app1 = PyQt.ensure_app()
        >>> app2 = PyQt.ensure_app()
        >>> assert app1 is app2

    """
    def __init__(PyQt):
        logger.debug('Constructing PyQt Wrapper')
        try:
            from PyQt5 import QtWidgets  # NOQA
            from PyQt5 import QtCore  # NOQA
        except ImportError as ex5:
            logger.debug('Could not find PyQt5')
            try:
                from PyQt4 import QtGui as QtWidgets
                from PyQt4 import QtCore
            except ImportError:
                logger.debug('Could not find PyQt4 or PyQt5')
                raise ex5
            else:
                logger.debug('Using PyQt4')
        else:
            logger.debug('Using PyQt5')
        PyQt.QtWidgets = QtWidgets
        PyQt.QtCore = QtCore
        PyQt.app = None

    def ensure_app(PyQt):
        if PyQt.app is None:
            # ensure we have a qt application
            app = PyQt.QtCore.QCoreApplication.instance()
            if app is None:  # if not in qtconsole
                app = PyQt.QtWidgets.QApplication(sys.argv)
            PyQt.app = app
        return PyQt.app


def import_pyqt():
    global __PyQt__
    if __PyQt__ is None:
        __PyQt__ = _PyQtWraper()
        __PyQt__.ensure_app()
    return __PyQt__


def lorium_ipsum():
    """ Standard testing string """
    ipsum_str = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
    do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
    minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex
    ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
    velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
    cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
    est laborum.
    '''
    return ipsum_str


def _ensure_clipboard_backend():
    """

    CommandLine:
        pip install pyperclip
        sudo apt-get install xclip
        sudo apt-get install xsel
        pip install PyQt5

        # for windows
        conda install pyqt

    References:
        http://stackoverflow.com/questions/11063458/-text-to-clipboard
        http://stackoverflow.com/questions/579687using-python

    Benchmark:
        import pyperclip
        import timerit
        ti = timerit.Timerit(verbose=2, unit='ms')
        # Qt is by far the fastest, followed by xsel, and then xclip
        backend_order = ['xclip', 'xsel', 'qt', 'gtk']
        backend_order = ['qt', 'xsel', 'xclip', 'gtk']
        for be in backend_order:
            print('-----')
            print('be = %r' % (be,))
            try:
                pyperclip.set_clipboard(be)
                ti.reset('test-copy').call(lambda: pyperclip.copy('a line of reasonable length text'))
                ti.reset('test-paste').call(lambda: pyperclip.paste())
            except Exception:
                print('Backend failed: {}'.format(be))

    CommandLine:
        python -m vimtk.xctrl _ensure_clipboard_backend

    Example:
        >>> from vimtk.xctrl import *  # NOQA
        >>> import pytest
        >>> import pyperclip
        >>> result = _ensure_clipboard_backend()
        >>> try:
        >>>     prev = get_clipboard()
        >>> except pyperclip.PyperclipException:
        >>>     pytest.skip('no appropriate backend for pyperclip')
        >>> text1 = 'foobar'
        >>> text2 = 'bazbiz'
        >>> copy_text_to_clipboard(text1)
        >>> pasted1 = get_clipboard()
        >>> copy_text_to_clipboard(text2)
        >>> pasted2 = get_clipboard()
        >>> assert pasted1 == text1
        >>> assert pasted2 == text2
        >>> copy_text_to_clipboard(prev)
    """
    if getattr(pyperclip, '_vimtk_monkey_backend', 'no') != 'no':
        return

    def _check_clipboard_backend(backend):
        if backend == 'windows':
            return sys.platform.startswith('win32')
        if backend == 'qt':
            return (ub.modname_to_modpath('PyQt5') or
                    ub.modname_to_modpath('PyQt4'))
        elif backend == 'gtk':
            return ub.modname_to_modpath('gtk')
        else:
            return pyperclip._executable_exists(backend)

    if ub.WIN32:
        backend_order = ['windows', 'qt']
    else:
        backend_order = ['xclip', 'xsel', 'qt', 'gtk']
        #raise NotImplementedError('not on windows yet')

    for backend in backend_order:
        if _check_clipboard_backend(backend):
            if pyperclip is None:
                raise Exception(
                    'pyperclip is not appear to be installed. '
                    'See also: https://github.com/Erotemic/vimtk/issues/5')
            pyperclip.set_clipboard(backend)
            pyperclip._vimtk_monkey_backend = backend
            return
        else:
            print('warning %r not installed' % (backend,))


def copy_text_to_clipboard(text):
    """
    Copies text to the clipboard
    """
    _ensure_clipboard_backend()
    if pyperclip is None:
        raise Exception(
            'pyperclip is not appear to be installed. '
            'See also: https://github.com/Erotemic/vimtk/issues/5')
    pyperclip.copy(text)


def get_clipboard():
    """
    References:
        http://stackoverflow.com/questions/11063458/python-script-to-copy-text-to-clipboard
    """
    _ensure_clipboard_backend()
    if pyperclip is None:
        raise Exception(
            'pyperclip is not appear to be installed. '
            'See also: https://github.com/Erotemic/vimtk/issues/5')
    text = pyperclip.paste()
    return text


def _get_number_of_monitors():
    PyQt = import_pyqt()
    desktop = PyQt.QtWidgets.QDesktopWidget()
    if hasattr(desktop, 'numScreens'):
        n = desktop.numScreens()
    else:
        n = desktop.screenCount()
    return n


def get_resolution_info(monitor_num=0):
    r"""
    Args:
        monitor_num (int): (default = 0)

    Returns:
        dict: info

    CommandLine:
        python -m vimtk.xctrl get_resolution_info

    Example:
        >>> # xdoctest: +REQUIRES(module:PyQt5)
        >>> monitor_num = 1
        >>> for monitor_num in range(_get_number_of_monitors()):
        >>>     info = get_resolution_info(monitor_num)
        >>>     print('monitor(%d).info = %s' % (monitor_num, ub.repr2(info, precision=3)))
    """
    # screen_resolution = app.desktop().screenGeometry()
    # width, height = screen_resolution.width(), screen_resolution.height()
    # print('height = %r' % (height,))
    # print('width = %r' % (width,))
    PyQt = import_pyqt()

    desktop = PyQt.QtWidgets.QDesktopWidget()
    screen = desktop.screen(monitor_num)
    ppi_x = screen.logicalDpiX()
    ppi_y = screen.logicalDpiY()
    dpi_x = screen.physicalDpiX()
    dpi_y = screen.physicalDpiY()
    # This call is not rotated correctly
    # rect = screen.screenGeometry()

    # This call has bad offsets
    rect = desktop.screenGeometry(screen=monitor_num)

    # This call subtracts offsets weirdly
    # desktop.availableGeometry(screen=monitor_num)

    pixels_w = rect.width()
    # for num in range(desktop.screenCount()):
    # pass
    pixels_h = rect.height()
    # + rect.y()

    """
    I have two monitors (screens), after rotation effects they have
    the geometry: (for example)
        S1 = {x: 0, y=300, w: 1920, h:1080}
        S2 = {x=1920, y=0, w: 1080, h:1920}

    Here is a pictoral example
    G--------------------------------------C-------------------
    |                                      |                  |
    A--------------------------------------|                  |
    |                                      |                  |
    |                                      |                  |
    |                                      |                  |
    |                 S1                   |                  |
    |                                      |        S2        |
    |                                      |                  |
    |                                      |                  |
    |                                      |                  |
    |--------------------------------------B                  |
    |                                      |                  |
    |                                      |                  |
    ----------------------------------------------------------D
    Desired Info

    G = (0, 0)
    A = (S1.x, S1.y)
    B = (S1.x + S1.w, S1.y + S1.h)

    C = (S2.x, S2.y)
    D = (S2.x + S1.w, S2.y + S2.h)

    from PyQt4 import QtGui, QtCore
    app = QtCore.QCoreApplication.instance()
    if app is None:
        import sys
        app = QtGui.QApplication(sys.argv)
    desktop = QtGui.QDesktopWidget()
    rect1 = desktop.screenGeometry(screen=0)
    rect2 = desktop.screenGeometry(screen=1)
    """
    off_x = rect.x()
    off_y = rect.y()

    inches_w = (pixels_w / dpi_x)
    inches_h = (pixels_h / dpi_y)
    inches_diag = (inches_w ** 2 + inches_h ** 2) ** .5

    MM_PER_INCH = 25.4

    mm_w = inches_w * MM_PER_INCH
    mm_h = inches_h * MM_PER_INCH
    mm_diag = inches_diag * MM_PER_INCH

    ratio = min(mm_w, mm_h) / max(mm_w, mm_h)

    #pixel_density = dpi_x / ppi_x
    info = ub.odict([
        ('monitor_num', monitor_num),
        ('off_x', off_x),
        ('off_y', off_y),
        ('ratio', ratio),
        ('ppi_x', ppi_x),
        ('ppi_y', ppi_y),
        ('dpi_x', dpi_x),
        ('dpi_y', dpi_y),
        #'pixel_density', pixel_density),
        ('inches_w', inches_w),
        ('inches_h', inches_h),
        ('inches_diag', inches_diag),
        ('mm_w', mm_w),
        ('mm_h', mm_h),
        ('mm_diag', mm_diag),
        ('pixels_w', pixels_w),
        ('pixels_h', pixels_h),
    ])
    return info


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m vimtk.cplat
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
