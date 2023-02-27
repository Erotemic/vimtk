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

from vimtk.core import *
