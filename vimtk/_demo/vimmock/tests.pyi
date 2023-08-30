import unittest
from _typeshed import Incomplete


class TestVimMock(unittest.TestCase):
    vim: Incomplete

    def setUp(self) -> None:
        ...

    def test_init(self) -> None:
        ...

    def test_setup_text(self) -> None:
        ...

    def test_open_file(self) -> None:
        ...

    def test_eval(self) -> None:
        ...


class TestBufferMock(unittest.TestCase):
    buffer: Incomplete

    def setUp(self) -> None:
        ...

    def test_getitem(self) -> None:
        ...

    def test_getitem_range(self) -> None:
        ...

    def test_setitem(self) -> None:
        ...

    def test_setitem_range(self) -> None:
        ...

    def test_setup_text(self) -> None:
        ...

    def test_append(self) -> None:
        ...


class TestCurrentMock(unittest.TestCase):
    current: Incomplete

    def setUp(self) -> None:
        ...

    def test_init(self) -> None:
        ...


class TestPatch(unittest.TestCase):

    def test_patch_vim(self) -> None:
        ...
