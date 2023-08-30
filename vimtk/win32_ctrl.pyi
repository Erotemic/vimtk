import ubelt as ub
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any

logger: Incomplete


class Win32Window(ub.NiceRepr):
    hwnd: Incomplete

    def __init__(self, hwnd) -> None:
        ...

    def __nice__(self):
        ...

    def title(self):
        ...

    def process_id(self):
        ...

    def visible(self):
        ...

    def process(self):
        ...

    def process_name(self):
        ...

    def info(self):
        ...

    def focus(self) -> None:
        ...


def send_keys(keys) -> None:
    ...


def find_window(proc: Incomplete | None = ...,
                title: Incomplete | None = ...,
                visible: bool = ...):
    ...


def find_windows(proc: Incomplete | None = ...,
                 title: Incomplete | None = ...,
                 visible: bool = ...) -> Generator[Any, None, None]:
    ...


def current_window_name():
    ...


def windows_in_order() -> Generator[Any, None, None]:
    ...


def findall_window_ids() -> None:
    ...
