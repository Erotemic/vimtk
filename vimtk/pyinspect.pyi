from _typeshed import Incomplete


def check_module_installed(modname: str) -> bool:
    ...


def in_pythonpath(modname):
    ...


def parse_import_names(sourcecode: str,
                       top_level: bool = ...,
                       fpath: Incomplete | None = ...,
                       branch: bool = ...) -> list:
    ...


def parse_function_names(sourcecode: str,
                         top_level: bool = ...,
                         ignore_condition: int = ...) -> list:
    ...
