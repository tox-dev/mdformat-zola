"""Full Zola feature matrix with multiple examples per construct.

Formats through every bundled extension, matching how the `mdformat` CLI runs on a real Zola site, so the Zola-specific
rules are exercised alongside GFM, footnotes, definition lists, alerts, and TOML frontmatter.
"""

from __future__ import annotations

from textwrap import dedent

import mdformat
import mdformat.plugins
import pytest

_EXTENSIONS = sorted(mdformat.plugins.PARSER_EXTENSIONS)


def fmt(text: str, *, wrap: int | str = 120) -> str:
    return mdformat.text(text, options={"wrap": wrap}, extensions=_EXTENSIONS)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param('{{ f(a="x") }}\n', '{{ f(a="x") }}\n', id="string_double"),
        pytest.param("{{ f(a='x') }}\n", '{{ f(a="x") }}\n', id="string_single_to_double"),
        pytest.param("{{ f(a='say \"hi\"') }}\n", "{{ f(a='say \"hi\"') }}\n", id="string_keep_single"),
        pytest.param("{{ f(a=`\"x\" 'y'`) }}\n", "{{ f(a=`\"x\" 'y'`) }}\n", id="string_backtick"),
        pytest.param("{{ f(a=true, b=false) }}\n", "{{ f(a=true, b=false) }}\n", id="bool"),
        pytest.param("{{ f(a=42) }}\n", "{{ f(a=42) }}\n", id="int"),
        pytest.param("{{ f(a=-7) }}\n", "{{ f(a=-7) }}\n", id="negative_int"),
        pytest.param("{{ f(a=1.5) }}\n", "{{ f(a=1.5) }}\n", id="float"),
        pytest.param("{{ f(a=-0.25) }}\n", "{{ f(a=-0.25) }}\n", id="negative_float"),
        pytest.param("{{ f(a=[1, 2, 3]) }}\n", "{{ f(a=[1, 2, 3]) }}\n", id="array_ints"),
        pytest.param("{{ f(a=[ 1,2 , 3 ]) }}\n", "{{ f(a=[1, 2, 3]) }}\n", id="array_whitespace"),
        pytest.param('{{ f(a=["x", true, 3]) }}\n', '{{ f(a=["x", true, 3]) }}\n', id="array_mixed"),
        pytest.param("{{ f(a=[]) }}\n", "{{ f(a=[]) }}\n", id="array_empty"),
        pytest.param("{{ f(z=1, a=2, m=3) }}\n", "{{ f(a=2, m=3, z=1) }}\n", id="args_sorted"),
    ],
)
def test_inline_value_types(text: str, expected: str) -> None:
    assert fmt(text, wrap="keep") == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("# H {{ f(b=2, a=1) }}\n", "# H {{ f(a=1, b=2) }}\n", id="heading"),
        pytest.param("- item {{ f(b=2, a=1) }}\n", "- item {{ f(a=1, b=2) }}\n", id="list"),
        pytest.param("> quote {{ f(b=2, a=1) }}\n", "> quote {{ f(a=1, b=2) }}\n", id="blockquote"),
        pytest.param("*em {{ f(b=2, a=1) }}*\n", "*em {{ f(a=1, b=2) }}*\n", id="emphasis"),
        pytest.param("[{{ f(b=2, a=1) }}](@/p.md)\n", "[{{ f(a=1, b=2) }}](@/p.md)\n", id="link_label"),
        pytest.param(
            "| {{ f(b=2, a=1) }} | x |\n| - | - |\n| 1 | 2 |\n",
            "| {{ f(a=1, b=2) }} | x   |\n| ----------------- | --- |\n| 1                 | 2   |\n",
            id="table_cell",
        ),
    ],
)
def test_inline_placement(text: str, expected: str) -> None:
    assert fmt(text) == expected


def test_inline_multiline_collapses() -> None:
    start = "a {{ f(\n  b=2,\n  a=1\n) }} b\n"
    assert fmt(start) == "a {{ f(a=1, b=2) }} b\n"


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("{{ not a shortcode }}\n", id="prose"),
        pytest.param("{{ f(a=) }}\n", id="missing_value"),
        pytest.param("text {{ and }} more\n", id="bare_braces"),
    ],
)
def test_invalid_inline_untouched(text: str) -> None:
    assert fmt(text) == text


@pytest.mark.parametrize(
    "body",
    [
        pytest.param('graph TD\n  A["x[1]"] --> B[*]\n  A --> C', id="mermaid_brackets_stars"),
        pytest.param(
            "line one\n\nline two with a very long tail that would wrap past one hundred twenty columns for sure",
            id="prose_not_reflowed",
        ),
        pytest.param("```python\nx = [1, *rest]\n```", id="code_fence_inside"),
        pytest.param("- a\n- b\n\n  indented", id="list_and_indent"),
        pytest.param("<div>\n  raw *html*\n</div>", id="raw_html"),
    ],
)
def test_block_body_verbatim(body: str) -> None:
    start = f"{{% demo() %}}\n{body}\n{{% end %}}\n"
    assert fmt(start) == start


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("{% q(b=2, a=1) %}\nx\n{% end %}\n", "{% q(a=1, b=2) %}\nx\n{% end %}\n", id="args_sorted"),
        pytest.param("{%/* q() */%}\n*raw*\n{%/* end */%}\n", "{%/* q() */%}\n*raw*\n{%/* end */%}\n", id="escaped"),
        pytest.param("{% q(\n  a=1\n) %}\nx\n{% end %}\n", "{% q(a=1) %}\nx\n{% end %}\n", id="multiline_start"),
        pytest.param(
            "{% a() %}\no\n{% b() %}\ni\n{% end %}\nc\n{% end %}\n",
            "{% a() %}\no\n{% b() %}\ni\n{% end %}\nc\n{% end %}\n",
            id="nested",
        ),
        pytest.param("{% a() %}\n{% end %}\n", "{% a() %}\n{% end %}\n", id="empty_body"),
    ],
)
def test_block_forms(text: str, expected: str) -> None:
    assert fmt(text) == expected


@pytest.mark.parametrize("level", range(1, 7))
def test_heading_attrs_all_levels(level: int) -> None:
    hashes = "#" * level
    assert fmt(f"{hashes} Title {{.b #id .a}}\n") == f"{hashes} Title {{#id .a .b}}\n"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("# T {#x}\n", "# T {#x}\n", id="id_only"),
        pytest.param("# T {.b .a .c}\n", "# T {.a .b .c}\n", id="classes_sorted"),
        pytest.param("# T {.z #id .a k=v}\n", "# T {#id .a .z k=v}\n", id="all_kinds"),
        pytest.param("# T {  #id   .a  }\n", "# T {#id .a}\n", id="whitespace"),
        pytest.param('# T {k="a b"}\n', '# T {k="a b"}\n', id="quoted_value"),
        pytest.param("# T {{ f() }} {#id}\n", "# T {{ f() }} {#id}\n", id="shortcode_then_attrs"),
        pytest.param("# Plain\n", "# Plain\n", id="no_attrs"),
        pytest.param("# T {not attrs}\n", "# T {not attrs}\n", id="invalid_block"),
    ],
)
def test_heading_attrs(text: str, expected: str) -> None:
    assert fmt(text) == expected


@pytest.mark.parametrize(
    ("info", "expected_info"),
    [
        pytest.param("rust", "rust", id="plain"),
        pytest.param("rust,linenos", "rust,linenos", id="linenos"),
        pytest.param("rust,linenos,linenostart=20", "rust,linenos,linenostart=20", id="linenostart"),
        pytest.param("rust,hl_lines=1 3-5", "rust,hl_lines=1 3-5", id="hl_lines"),
        pytest.param("rust,hide_lines=2 7", "rust,hide_lines=2 7", id="hide_lines"),
        pytest.param("rust,name=mod.rs", "rust,name=mod.rs", id="name"),
        pytest.param(
            "scss, linenos, linenostart=10, hl_lines=3-4 8-9, hide_lines=2 7",
            "scss,linenos,linenostart=10,hl_lines=3-4 8-9,hide_lines=2 7",
            id="all_options",
        ),
        pytest.param("rust, hl_lines=1  2 ,linenos", "rust,linenos,hl_lines=1 2", id="reordered"),
        pytest.param("rust,custom", "rust,custom", id="unknown_kept"),
    ],
)
def test_fence_annotations(info: str, expected_info: str) -> None:
    assert fmt(f"```{info}\nlet x = 1;\n```\n") == f"```{expected_info}\nlet x = 1;\n```\n"


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("[a](@/pages/about.md)\n", id="internal"),
        pytest.param("[a](@/pages/about.md#anchor)\n", id="internal_anchor"),
        pytest.param("See [the guide](@/docs/_index.md) for more.\n", id="internal_in_text"),
        pytest.param("[colocated](image.png)\n", id="colocated_asset"),
    ],
)
def test_internal_links_preserved(text: str) -> None:
    assert fmt(text) == text


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("Intro.\n\n<!-- more -->\n\nBody.\n", id="spaced"),
        pytest.param("Intro.\n\n<!--more-->\n\nBody.\n", id="tight"),
    ],
)
def test_summary_delimiter_preserved(text: str) -> None:
    assert fmt(text) == text


def test_toml_frontmatter_preserved() -> None:
    start = dedent("""\
        +++
        title = "Post"
        date = 2024-01-02
        weight = 3
        +++

        Body.
        """)
    assert fmt(start) == start


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(
            "| a | b |\n|---|---|\n| 1 | 2 |\n",
            "| a   | b   |\n| --- | --- |\n| 1   | 2   |\n",
            id="table",
        ),
        pytest.param("this is ~~gone~~ text\n", "this is ~~gone~~ text\n", id="strikethrough"),
        pytest.param("- [ ] todo\n- [x] done\n", "- [ ] todo\n- [x] done\n", id="task_list"),
        pytest.param("A note.[^1]\n\n[^1]: The note.\n", "A note.[^1]\n\n[^1]: The note.\n", id="footnote"),
        pytest.param("Term\n: Definition\n", "Term\n: Definition\n", id="definition_list"),
        pytest.param("> [!NOTE]\n> Heads up.\n", "> [!NOTE]\n> Heads up.\n", id="gfm_alert"),
    ],
)
def test_bundled_gfm_features(text: str, expected: str) -> None:
    assert fmt(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("{{ variable }}\n", id="bare_tera_var"),
        pytest.param("text {# comment #} more\n", id="tera_comment"),
        pytest.param("{% end %}\n", id="stray_end"),
    ],
)
def test_non_shortcode_directives_left_literal(text: str) -> None:
    assert fmt(text) == text
