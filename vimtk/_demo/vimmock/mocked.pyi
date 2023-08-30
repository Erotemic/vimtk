import ubelt as ub
from _typeshed import Incomplete


class VimErrorMock(Exception):
    ...


class LineMock:
    ...


def classname(obj):
    ...


class BufferMock(ub.NiceRepr):
    name: str
    number: int
    range: Incomplete
    valid: bool

    def __init__(self, text: Incomplete | None = ...) -> None:
        ...

    def __nice__(self):
        ...

    def mark(self, key):
        ...

    def __delitem__(self, key) -> None:
        ...

    def __getitem__(self, key):
        ...

    def __setitem__(self, key, value) -> None:
        ...

    def __len__(self):
        ...

    def setup_text(self,
                   text: Incomplete | None = ...,
                   name: str = ...) -> None:
        ...

    def open_file(self, filepath) -> None:
        ...

    def append(self, other) -> None:
        ...


class WindowMock:
    cursor: Incomplete

    def __init__(self, cursor: Incomplete | None = ...) -> None:
        ...


class RangeMock:
    ...


class TabPageMock:
    ...


class CurrentMock:
    line: Incomplete
    buffer: Incomplete
    window: Incomplete
    range: Incomplete
    tabpage: Incomplete

    def __init__(self, text: Incomplete | None = ...) -> None:
        ...


class VimMock:
    VAR_DEF_SCOPE: int
    VAR_FIXED: int
    VAR_LOCKED: int
    VAR_SCOPE: int
    VIM_SPECIAL_PATH: str
    Buffer = BufferMock
    Range = RangeMock
    TabPage = TabPageMock
    Window = WindowMock
    error = VimErrorMock
    vim_mode_codes: Incomplete
    current: Incomplete
    buffers: Incomplete
    windows: Incomplete
    tabpages: Incomplete
    global_variables: Incomplete

    def __init__(self) -> None:
        ...

    def setup_text(self, text, name: str = ...) -> None:
        ...

    def move_cursor(self, row, col: int = ...) -> None:
        ...

    def open_file(self, filepath, cursor: Incomplete | None = ...) -> None:
        ...

    def command(self, command) -> None:
        ...

    def eval(self, command):
        ...
