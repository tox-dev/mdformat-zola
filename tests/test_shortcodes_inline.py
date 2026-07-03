from __future__ import annotations

from textwrap import dedent

import mdformat
import pytest


def _fmt(text: str, wrap: int | str = "keep") -> str:
    return mdformat.text(text, options={"wrap": wrap}, extensions=["zola"])


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param('{{ youtube(id="x") }}\n', '{{ youtube(id="x") }}\n', id="simple"),
        pytest.param("{{  youtube( id='x' ) }}\n", '{{ youtube(id="x") }}\n', id="normalized"),
        pytest.param(
            '{{ youtube(id="x", autoplay=true) }}\n',
            '{{ youtube(autoplay=true, id="x") }}\n',
            id="args_sorted",
        ),
        pytest.param('{{/* youtube(id="x") */}}\n', '{{/* youtube(id="x") */}}\n', id="escaped"),
        pytest.param('a {{ ref(page="x") }} b\n', 'a {{ ref(page="x") }} b\n', id="in_paragraph"),
    ],
)
def test_inline_shortcode(text: str, expected: str) -> None:
    assert _fmt(text) == expected


def test_inline_shortcode_not_wrapped() -> None:
    start = (
        'Prefix {{ screen(name="project", alt="A very long alt text that certainly goes well beyond '
        'the one hundred and twenty character wrap boundary for sure") }} suffix\n'
    )
    outcome = _fmt(start, wrap=120)
    shortcode_line = next(line for line in outcome.splitlines() if line.startswith("{{"))
    assert shortcode_line == (
        '{{ screen(alt="A very long alt text that certainly goes well beyond the one hundred and '
        'twenty character wrap boundary for sure", name="project") }}'
    )


def test_inline_shortcode_escaping_not_applied() -> None:
    assert _fmt("x {{/* note() */}} y\n") == "x {{/* note() */}} y\n"


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("{{ not a shortcode }}\n", id="invalid_call"),
        pytest.param("{{ foo }}\n", id="missing_parens"),
        pytest.param("text {{ and }} more\n", id="bare_double_braces"),
    ],
)
def test_inline_shortcode_invalid_left_untouched(text: str) -> None:
    assert _fmt(text) == text


def test_inline_shortcode_unterminated_is_text() -> None:
    assert _fmt("a {{ foo(x=1)\n") == "a {{ foo(x=1)\n"


def test_inline_shortcode_unterminated_string_is_text() -> None:
    assert _fmt('{{ foo(a="x) }}\n') == '{{ foo(a="x) }}\n'


def test_inline_shortcode_in_link_label() -> None:
    start = '[{{ icon(name="x") }}](@/page.md)\n'
    assert _fmt(start) == start


def test_inline_shortcode_in_list() -> None:
    start = """\
        - Item 1 {{ ref(page="1") }}
        - Item 2 {{ ref(page="2") }}
        """
    assert _fmt(dedent(start)) == dedent(start)
