from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("# Title {#manual}\n", "# Title {#manual}\n", id="id"),
        pytest.param("# Title {.header .bold}\n", "# Title {.bold .header}\n", id="classes_sorted"),
        pytest.param(
            "# Title {.zebra #manual .apple}\n",
            "# Title {#manual .apple .zebra}\n",
            id="id_first_classes_sorted",
        ),
        pytest.param("##  Spaced   {#id}\n", "## Spaced {#id}\n", id="heading_whitespace"),
        pytest.param("# Title {  #id   .a  }\n", "# Title {#id .a}\n", id="attr_whitespace"),
    ],
)
def test_heading_attrs_normalized(fmt: Callable[..., str], text: str, expected: str) -> None:
    assert fmt(text) == expected


def test_heading_with_inline_shortcode_and_attrs(fmt: Callable[..., str]) -> None:
    start = '# Heading with {{ icon(name="x") }} {#id .c}\n'
    assert fmt(start) == start


def test_heading_with_only_inline_shortcode_untouched(fmt: Callable[..., str]) -> None:
    start = '# Heading with {{ icon(name="x") }}\n'
    assert fmt(start) == start


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("# Plain heading\n", id="no_attrs"),
        pytest.param("# Trailing brace {not attrs!}\n", id="invalid_attr_block"),
        pytest.param("# Empty {}\n", id="empty_attr_block"),
    ],
)
def test_heading_left_untouched(fmt: Callable[..., str], text: str) -> None:
    assert fmt(text) == text
