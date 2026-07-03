from __future__ import annotations

from textwrap import dedent

import mdformat
import pytest


def _fmt(text: str, wrap: int | str = 120) -> str:
    return mdformat.text(text, options={"wrap": wrap}, extensions=["zola"])


def test_block_body_preserved_verbatim() -> None:
    start = """\
        {% mermaid() %}
        graph TD
          A["velodex[x]"] --> B[*]
          A --> C
        {% end %}
        """
    assert _fmt(dedent(start)) == dedent(start)


def test_block_start_args_sorted_body_kept() -> None:
    long_body = "body *keeps* [markdown](y) then " + "more words that push well past column one twenty " * 3
    assert len(long_body) > 120
    start = '{% quote(cls="x", author="Bob") %}\n' + long_body + "\n{% end %}\n"
    expected = '{% quote(author="Bob", cls="x") %}\n' + long_body + "\n{% end %}\n"
    assert _fmt(start) == expected


def test_block_escaped() -> None:
    start = """\
        {%/* quote() */%}
        not *rendered*
        {%/* end */%}
        """
    assert _fmt(dedent(start)) == dedent(start)


def test_block_nested() -> None:
    start = """\
        {% outer() %}
        before
        {% inner() %}
        deep
        {% end %}
        after
        {% end %}
        """
    assert _fmt(dedent(start)) == dedent(start)


def test_block_empty_body() -> None:
    start = """\
        {% note() %}
        {% end %}
        """
    assert _fmt(dedent(start)) == dedent(start)


def test_block_terminates_paragraph() -> None:
    start = """\
        text before
        {% note(id="x") %}
        body
        {% end %}
        """
    expected = """\
        text before

        {% note(id="x") %}
        body
        {% end %}
        """
    assert _fmt(dedent(start)) == dedent(expected)


def test_block_body_with_foreign_marker_kept() -> None:
    start = """\
        {% x() %}
        {%/* end */%}
        {% end %}
        """
    assert _fmt(dedent(start)) == dedent(start)


def test_block_too_short_marker_is_text() -> None:
    assert _fmt("{%}\n") == "{%}\n"


def test_block_multiline_start_tag_collapses() -> None:
    start = """\
        {% quote(
          author="Bob",
          cite="x"
        ) %}
        body stays put
        {% end %}
        """
    expected = """\
        {% quote(author="Bob", cite="x") %}
        body stays put
        {% end %}
        """
    assert _fmt(dedent(start)) == dedent(expected)


def test_block_unclosed_start_tag_is_text() -> None:
    assert _fmt("{% quote(\nnever closed here\n") == "{% quote( never closed here\n"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("{% quote() %}\nno end here\n", "{% quote() %} no end here\n", id="unterminated"),
        pytest.param(
            "{% invalid here %}\nbody\n{% end %}\n",
            "{% invalid here %} body {% end %}\n",
            id="invalid_start",
        ),
    ],
)
def test_block_not_recognized(text: str, expected: str) -> None:
    assert _fmt(text) == expected


def test_block_in_list_indented_body() -> None:
    start = """\
        - item

          {% note() %}
          body
          {% end %}
        """
    assert _fmt(dedent(start)) == dedent(start)
