from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def test_zola_document_with_all_features(fmt: Callable[..., str]) -> None:
    start = """\
        +++
        title = "Post"
        weight = 3
        +++

        ## Section {.lead #intro}

        Text with {{  ref( path="page.md" ) }} inline shortcode.

        {% note(kind="warning") %}
        Body with *emphasis* and an [internal link](@/other.md).
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
        Body with *emphasis* and an [internal link](@/other.md).
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
    assert fmt(dedent(start)) == dedent(expected)


def test_document_is_idempotent(fmt: Callable[..., str]) -> None:
    start = """\
        # Heading {.b .a}

        {{ youtube(id="x", autoplay=true) }}

        {% quote(cite="me") %}
        content
        {% end %}
        """
    once = fmt(dedent(start))
    assert fmt(once) == once
