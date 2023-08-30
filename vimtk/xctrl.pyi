import ubelt as ub
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any

logger: Incomplete


def is_directory_open(dpath):
    ...


def wmctrl_list():
    ...


def windows_in_order() -> Generator[Any, None, None]:
    ...


def find_windows(proc: Incomplete | None = ...,
                 title: Incomplete | None = ...,
                 visible: bool = ...) -> Generator[Any, None, None]:
    ...


class XWindow(ub.NiceRepr):
    wm_id: Incomplete
    cache: Incomplete
    sleeptime: float

    def __init__(self,
                 wm_id,
                 info: Incomplete | None = ...,
                 sleeptime: float = ...) -> None:
        ...

    @classmethod
    def find(XWindow, pattern, method: str = ...):
        ...

    @classmethod
    def current(XWindow):
        ...

    @property
    def hexid(self):
        ...

    def title(self) -> None:
        ...

    def visible(self):
        ...

    def __nice__(self):
        ...

    def wm_class(self):
        ...

    def process(self):
        ...

    def size(self):
        ...

    def resize(self, width, height) -> None:
        ...

    def wininfo(self):
        ...

    def process_name(self):
        ...

    def focus(self, sleeptime: Incomplete | None = ...) -> None:
        ...

    def info(self):
        ...

    def move(self, bbox):
        ...


class XCtrl:

    @classmethod
    def cmd(XCtrl, command):
        ...

    @classmethod
    def findall_window_ids(XCtrl, pattern):
        ...

    @classmethod
    def sort_window_ids(XCtrl, winid_list, order: str = ...):
        ...

    @staticmethod
    def killold(pattern, num: int = ...) -> None:
        ...

    @staticmethod
    def sorted_window_ids(order: str = ...):
        ...

    @staticmethod
    def find_window_id(pattern, method: str = ..., error: str = ...):
        ...

    @staticmethod
    def current_gvim_edit(op: str = ..., fpath: str = ...) -> None:
        ...

    @staticmethod
    def copy_gvim_to_terminal_script(text,
                                     return_to_win: str = ...,
                                     verbose: int = ...,
                                     sleeptime: float = ...) -> None:
        ...

    @staticmethod
    def do(*cmd_list, **kwargs) -> None:
        ...

    @staticmethod
    def current_window_id():
        ...

    @staticmethod
    def current_window_name():
        ...

    @staticmethod
    def focus_window(winhandle,
                     path: Incomplete | None = ...,
                     name: Incomplete | None = ...,
                     sleeptime: float = ...) -> None:
        ...

    @classmethod
    def send_keys(XCtrl, key, sleeptime: float = ...) -> None:
        ...
