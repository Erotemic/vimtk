from os import PathLike
from _typeshed import Incomplete

import vimtk._demo.vimmock

logger: Incomplete
__docstubs__: str


def mockvim(fpath: PathLike | None = None,
            text: str | None = None) -> vimtk._demo.vimmock.mocked.VimMock:
    ...


def reload_vimtk() -> None:
    ...


reload = reload_vimtk


class Config:
    default: Incomplete
    state: Incomplete

    def __init__(self) -> None:
        ...

    def __getitem__(self, key):
        ...

    def __setitem__(self, key, value) -> None:
        ...

    def get(self, key, default: Incomplete | None = ..., context: str = ...):
        ...


class Clipboard:

    @staticmethod
    def copy(text):
        ...

    @staticmethod
    def paste():
        ...


class TextSelector:

    @staticmethod
    def current_indent(url_ok: bool = ...):
        ...

    @staticmethod
    def word_at_cursor(url_ok: bool = ...):
        ...

    @staticmethod
    def get_word_in_line_at_col(line: str,
                                col: int,
                                nonword_chars_left: str = ...,
                                nonword_chars_right: Incomplete | None = ...):
        ...

    @staticmethod
    def selected_text(select_at_cursor: bool = ...):
        ...

    @staticmethod
    def text_between_lines(lnum1, lnum2, col1: int = ..., col2=...):
        ...

    @staticmethod
    def line_at_cursor():
        ...

    @staticmethod
    def paragraph_range_at_cursor():
        ...


class CursorContext:
    pos: Incomplete
    offset: Incomplete

    def __init__(self, offset: int = ...) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, *exc_info) -> None:
        ...


class Cursor:

    @staticmethod
    def move(row, col: int = ...) -> None:
        ...

    @staticmethod
    def position():
        ...


class TextInsertor:

    def overwrite(text) -> None:
        ...

    @staticmethod
    def insert_at(text, pos) -> None:
        ...

    @staticmethod
    def insert_under_cursor(text) -> None:
        ...

    @staticmethod
    def insert_above_cursor(text) -> None:
        ...

    @staticmethod
    def insert_over_selection(text) -> None:
        ...

    @staticmethod
    def insert_between_lines(text, row1, row2) -> None:
        ...


class Mode:
    vim_mode_codes: Incomplete

    @staticmethod
    def current():
        ...

    @staticmethod
    def ensure_normal() -> None:
        ...


class Python:

    @staticmethod
    def current_module_info():
        ...

    @staticmethod
    def is_module_pythonfile():
        ...

    @staticmethod
    def find_import_row():
        ...

    @staticmethod
    def prepend_import_block(text) -> None:
        ...

    @staticmethod
    def format_text_as_docstr(text):
        ...

    @staticmethod
    def unformat_text_as_docstr(formated_text):
        ...

    @staticmethod
    def find_func_above_row(row: str = ..., maxIter: int = ...):
        ...


def sys_executable():
    ...


def preprocess_executable_text(text):
    ...


def execute_text_in_terminal(text, return_to_vim: bool = ...) -> None:
    ...


def vim_argv(defaults: Incomplete | None = ...):
    ...


def get_current_fpath():
    ...


def get_current_filetype():
    ...


def ensure_normalmode():
    ...


def autogen_imports(fpath_or_text):
    ...


def is_url(text):
    ...


def extract_url_embeding(word):
    ...


def find_and_open_path(path,
                       mode: str = ...,
                       verbose: int = ...,
                       enable_python: bool = ...,
                       enable_url: bool = ...,
                       enable_cli: bool = ...):
    ...


def open_path(fpath,
              mode: str = ...,
              nofoldenable: bool = ...,
              verbose: int = ...) -> None:
    ...


def find_pattern_above_row(pattern,
                           line_list: str = ...,
                           row: str = ...,
                           maxIter: int = ...):
    ...


def get_first_nonempty_line_after_cursor():
    ...


def get_indentation(line_):
    ...


def get_minimum_indentation(text: str) -> int:
    ...


CONFIG: Incomplete
