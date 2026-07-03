from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import mdformat
import mdformat.plugins

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pytest_mock import MockerFixture


def _fmt(text: str, *, codeformatters: Sequence[str] = ()) -> str:
    return mdformat.text(dedent(text), extensions=["zola"], codeformatters=codeformatters)


def test_fence_plain_language_untouched() -> None:
    start = """\
        ```python
        x = 1
        ```
        """
    assert _fmt(start) == dedent(start)


def test_fence_annotations_reordered() -> None:
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
    assert _fmt(start) == dedent(expected)


def test_fence_unknown_annotation_preserved() -> None:
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
    assert _fmt(start) == dedent(expected)


def test_fence_backticks_in_code_grow_fence() -> None:
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
    assert _fmt(start) == dedent(expected)


def test_fence_backtick_in_info_uses_tilde() -> None:
    assert _fmt("~~~py`x\ncode\n~~~\n") == "~~~py`x\ncode\n~~~\n"


def test_fence_codeformatter_runs_with_zola_annotations() -> None:
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
    assert _fmt(start, codeformatters=["python"]) == dedent(expected)


def test_fence_codeformatter_output_gets_trailing_newline(mocker: MockerFixture) -> None:
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
    assert _fmt(start, codeformatters=["python"]) == dedent(expected)


def test_fence_codeformatter_error_keeps_source(mocker: MockerFixture) -> None:
    def boom(_code: str, _info: str) -> str:
        raise ValueError

    mocker.patch.dict(mdformat.plugins.CODEFORMATTERS, {"python": boom})
    start = """\
        ```python
        x=1
        ```
        """
    assert _fmt(start, codeformatters=["python"]) == dedent(start)
