from __future__ import annotations

from textwrap import dedent

import mdformat
import mdformat.plugins

# Mirror the CLI, which enables every installed plugin; the wheel pins exactly the bundled set.
_EXTENSIONS = sorted(mdformat.plugins.PARSER_EXTENSIONS)


def test_zola_document_with_all_features() -> None:
    start = """\
        +++
        title = "Post"
        weight = 3
        +++

        ## Section {.lead #intro}

        Text with {{  ref( path="page.md" ) }} inline shortcode.

        {% note(kind="warning") %}
        Body *stays* verbatim and [links](@/other.md) survive.
        {% end %}

        | a | b |
        |---|---|
        | 1 | 2 |

        > [!NOTE]
        > An alert.

        ```rust, linenos , hl_lines=1  2
        let x = 1;
        ```
        """
    expected = """\
        +++
        title = "Post"
        weight = 3
        +++

        ## Section {#intro .lead}

        Text with {{ ref(path="page.md") }} inline shortcode.

        {% note(kind="warning") %}
        Body *stays* verbatim and [links](@/other.md) survive.
        {% end %}

        | a   | b   |
        | --- | --- |
        | 1   | 2   |

        > [!NOTE]
        > An alert.

        ```rust,linenos,hl_lines=1 2
        let x = 1;
        ```
        """
    assert mdformat.text(dedent(start), options={"wrap": 120}, extensions=_EXTENSIONS) == dedent(expected)


def test_document_is_idempotent() -> None:
    start = """\
        # Heading {.b .a}

        {{ youtube(id="x", autoplay=true) }}

        {% quote(cite="me") %}
        content
        {% end %}
        """
    once = mdformat.text(dedent(start), options={"wrap": 120}, extensions=_EXTENSIONS)
    assert mdformat.text(once, options={"wrap": 120}, extensions=_EXTENSIONS) == once
