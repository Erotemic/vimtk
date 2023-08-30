"""
python -c "import ubelt._internal as a; a.autogen_init('vimtk', attrs=True)"

TODO: exclude backends like win32 and xctrl
mkinit ~/local/vim/vimfiles/bundle/vimtk/vimtk/__init__.py -w

Note:

Also change version in: ~/code/vimtk/plugin/vimtk.vim
And make notes in : ~/code/vimtk/CHANGELOG.md
"""
# flake8: noqa
__version__ = '0.4.0'

__submodules__ = ['core']

from vimtk.core import (CONFIG, Clipboard, Config, Cursor, CursorContext, Mode,
                        Python, TextInsertor, TextSelector, autogen_imports,
                        ensure_normalmode, execute_text_in_terminal,
                        extract_url_embeding, find_and_open_path,
                        find_pattern_above_row, get_current_filetype,
                        get_current_fpath,
                        get_first_nonempty_line_after_cursor, get_indentation,
                        get_minimum_indentation, is_url, logger, mockvim,
                        open_path, preprocess_executable_text, reload,
                        reload_vimtk, sys_executable, vim_argv,)

__all__ = ['CONFIG', 'Clipboard', 'Config', 'Cursor', 'CursorContext', 'Mode',
           'Python', 'TextInsertor', 'TextSelector', 'autogen_imports',
           'ensure_normalmode', 'execute_text_in_terminal',
           'extract_url_embeding', 'find_and_open_path',
           'find_pattern_above_row', 'get_current_filetype',
           'get_current_fpath', 'get_first_nonempty_line_after_cursor',
           'get_indentation', 'get_minimum_indentation', 'is_url', 'logger',
           'mockvim', 'open_path', 'preprocess_executable_text', 'reload',
           'reload_vimtk', 'sys_executable', 'vim_argv']
