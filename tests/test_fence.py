from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import mdformat.plugins

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_mock import MockerFixture


def test_fence_plain_language_untouched(fmt: Callable[..., str]) -> None:
    start = """\
        ```python
        x = 1
        ```
        """
    assert fmt(dedent(start)) == dedent(start)


def test_fence_annotations_reordered(fmt: Callable[..., str]) -> None:
    start = """\
        ```rust, hl_lines=3-4  8-9,linenos , linenostart=10
        let x = 1;
        ```
        """
    expected = """\
        ```rust,linenos,linenostart=10,hl_lines=3-4 8-9
        let x = 1;
        ```
        """
    assert fmt(dedent(start)) == dedent(expected)


def test_fence_unknown_annotation_preserved(fmt: Callable[..., str]) -> None:
    start = """\
        ```rust,custom=1,linenos
        let x = 1;
        ```
        """
    expected = """\
        ```rust,linenos,custom=1
        let x = 1;
        ```
        """
    assert fmt(dedent(start)) == dedent(expected)


def test_fence_backticks_in_code_grow_fence(fmt: Callable[..., str]) -> None:
    start = """\
        ```rust,linenos
        ```nested```
        ```
        """
    expected = """\
        ````rust,linenos
        ```nested```
        ````
        """
    assert fmt(dedent(start)) == dedent(expected)


def test_fence_backtick_in_info_uses_tilde(fmt: Callable[..., str]) -> None:
    assert fmt("~~~py`x\ncode\n~~~\n") == "~~~py`x\ncode\n~~~\n"


def test_fence_codeformatter_runs_with_zola_annotations(fmt: Callable[..., str]) -> None:
    start = """\
        ```python,linenos
        x=  1
        ```
        """
    expected = """\
        ```python,linenos
        x = 1
        ```
        """
    assert fmt(dedent(start), codeformatters=["python"]) == dedent(expected)


def test_fence_codeformatter_output_gets_trailing_newline(fmt: Callable[..., str], mocker: MockerFixture) -> None:
    mocker.patch.dict(mdformat.plugins.CODEFORMATTERS, {"python": lambda _code, _info: "formatted"})
    start = """\
        ```python
        x=1
        ```
        """
    expected = """\
        ```python
        formatted
        ```
        """
    assert fmt(dedent(start), codeformatters=["python"]) == dedent(expected)


def test_fence_codeformatter_error_keeps_source(fmt: Callable[..., str], mocker: MockerFixture) -> None:
    def boom(_code: str, _info: str) -> str:
        raise ValueError

    mocker.patch.dict(mdformat.plugins.CODEFORMATTERS, {"python": boom})
    start = """\
        ```python
        x=1
        ```
        """
    assert fmt(dedent(start), codeformatters=["python"]) == dedent(start)
