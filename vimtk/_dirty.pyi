from collections.abc import Generator
from typing import Any


def regex_reconstruct_split(pattern, text):
    ...


def msgblock(key, text, side: str = ...):
    ...


def get_indentation(line_):
    ...


def get_minimum_indentation(text: str) -> int:
    ...


def interleave(args: tuple) -> Generator[Any, None, None]:
    ...


def colorprint(text, color) -> None:
    ...


def format_single_paragraph_sentences(text: str,
                                      debug: bool = ...,
                                      myprefix: bool = ...,
                                      sentence_break: bool = ...,
                                      max_width: int = ...,
                                      sepcolon: bool = ...) -> str:
    ...


def format_multiple_paragraph_sentences(text, debug: bool = ..., **kwargs):
    ...
