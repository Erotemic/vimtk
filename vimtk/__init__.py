"""
python -c "import ubelt._internal as a; a.autogen_init('vimtk', attrs=True)"

TODO: exclude backends like win32 and xctrl
mkinit ~/local/vim/vimfiles/bundle/vimtk/vimtk/__init__.py -w

Note:

Also change version in: ~/code/vimtk/plugin/vimtk.vim
And make notes in : ~/code/vimtk/CHANGELOG.md
"""
# flake8: noqa
__version__ = '0.3.1'

from vimtk.core import *

# from vimtk import core
# from vimtk import cplat
# from vimtk import pyinspect
# from vimtk import win32_ctrl
# from vimtk import xctrl

# from vimtk.core import (CONFIG, Clipboard, Config, Cursor, CursorContext,
#                         Python, TextSelector, autogen_imports,
#                         ensure_normalmode, execute_text_in_terminal,
#                         get_current_fpath, logger, preprocess_executable_text,
#                         reload_vimtk, vim_argv,)
# from vimtk.cplat import (copy_text_to_clipboard, get_clipboard,
#                          get_resolution_info,
#                          import_pyqt, logger, lorium_ipsum,)
# from vimtk.pyinspect import (check_module_installed, in_pythonpath,
#                              parse_function_names, parse_import_names,)
# from vimtk.win32_ctrl import (Win32Window, current_window_name, find_window,
#                               find_windows, findall_window_ids, logger,
#                               send_keys, windows_in_order,)
# from vimtk.xctrl import (XCtrl, XWindow, find_windows, is_directory_open,
#                          logger, windows_in_order, wmctrl_list,)

# __all__ = ['CONFIG', 'Clipboard', 'Config', 'Cursor', 'CursorContext',
#            'Python', 'TextSelector', 'Win32Window', 'XCtrl', 'XWindow',
#            'autogen_imports', 'check_module_installed',
#            'copy_text_to_clipboard', 'core', 'cplat', 'current_window_name',
#            'ensure_normalmode', 'execute_text_in_terminal', 'find_window',
#            'find_windows', 'find_windows', 'findall_window_ids',
#            'get_clipboard', 'get_current_fpath',
#            'get_resolution_info', 'import_pyqt', 'in_pythonpath',
#            'is_directory_open', 'logger', 'logger', 'logger', 'logger',
#            'lorium_ipsum', 'parse_function_names', 'parse_import_names',
#            'preprocess_executable_text', 'pyinspect', 'reload_vimtk',
#            'send_keys', 'vim_argv', 'win32_ctrl', 'windows_in_order',
#            'windows_in_order', 'wmctrl_list', 'xctrl']
