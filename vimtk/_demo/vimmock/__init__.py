"""
vim mock object for easier testing of vim plugins written in Python.

Originally from https://github.com/Erotemic/vimmock/tree/buffer_filename
"""
from vimmock.mocked import VimMock


__all__ = ['VimMock', 'patch_vim']
__version__ = '0.2.0.dev'


def patch_vim():
    """
    Sets new ``VimMock`` instance under ``vim`` key within ``sys.modules``.
    """
    import sys
    vim = sys.modules['vim'] = VimMock()
    return vim
