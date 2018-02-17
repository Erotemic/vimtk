import sys
import pyperclip
import ubelt as ub


def _ensure_clipboard_backend():
    """

    CommandLine:
        pip install pyperclip
        sudo apt-get install xclip
        sudo apt-get install xsel

    References:
        http://stackoverflow.com/questions/11063458/-text-to-clipboard
        http://stackoverflow.com/questions/579687using-python

    Ignore:
        import pyperclip
        # Qt is by far the fastest, followed by xsel, and then xclip
        backend_order = ['xclip', 'xsel', 'qt', 'gtk']
        backend_order = ['qt', 'xsel', 'xclip', 'gtk']
        for be in backend_order:
            print('be = %r' % (be,))
            pyperclip.set_clipboard(be)
            %timeit pyperclip.copy('a line of reasonable length text')
            %timeit pyperclip.paste()
    """
    if getattr(pyperclip, '_vimtk_monkey_backend', 'no') != 'no':
        return

    def _check_clipboard_backend(backend):
        if backend == 'qt':
            return (ub.modname_to_modpath('PyQt5') or
                    ub.modname_to_modpath('PyQt4'))
        elif backend == 'gtk':
            return ub.modname_to_modpath('gtk')
        else:
            return pyperclip._executable_exists(backend)

    if sys.platform.startswith('win32'):
        raise NotImplementedError('not on windows yet')

    backend_order = ['xclip', 'xsel', 'qt', 'gtk']
    for backend in backend_order:
        if _check_clipboard_backend(backend):
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
    pyperclip.copy(text)
