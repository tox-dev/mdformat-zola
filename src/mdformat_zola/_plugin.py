"""Mdformat plugin interface for Zola markdown."""

from __future__ import annotations

__lazy_modules__ = [
    "argparse",
    f"{__spec__.parent}._mdit_plugins",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
    f"{__spec__.parent}._syntax",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

import argparse
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

    from markdown_it import MarkdownIt
    from mdformat.renderer.typing import Postprocess, Render

from ._mdit_plugins import shortcode_plugin
from ._renderer import postprocess_heading, render_fence, render_verbatim, render_zola_shortcode_block
from ._syntax import format_shortcode

#: Formatting rewrites the syntax tree, so mdformat skips its check that the output parses to the same tree.
CHANGES_AST: Final[bool] = True
#: Renderers for the token types this plugin adds or overrides, keyed by token type.
RENDERERS: Final[Mapping[str, Render]] = {
    "zola_shortcode": render_verbatim,
    "zola_shortcode_block": render_zola_shortcode_block,
    "fence": render_fence,
}
#: Postprocessors that adjust the rendered text of a token type, keyed by token type.
POSTPROCESSORS: Final[Mapping[str, Postprocess]] = {
    "heading": postprocess_heading,
}


def update_mdit(mdit: MarkdownIt) -> None:
    """Add Zola-specific markdown-it-py plugins."""
    mdit.use(shortcode_plugin, format_shortcode)


def add_cli_argument_group(group: argparse._ArgumentGroup) -> None:
    """Expose the shortcodes whose bodies should be formatted as Markdown."""
    group.add_argument(
        "--zola-markdown-shortcodes",
        dest="plugin.zola.markdown_shortcodes",
        metavar="NAMES",
        default=argparse.SUPPRESS,
        help="comma-separated shortcode names whose body is Markdown and should be formatted (bodies of any other "
        "shortcode, e.g. mermaid, are kept verbatim)",
    )


__all__ = [
    "CHANGES_AST",
    "POSTPROCESSORS",
    "RENDERERS",
    "add_cli_argument_group",
    "update_mdit",
]
