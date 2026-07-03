"""Mdformat plugin interface for Zola markdown."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

    from markdown_it import MarkdownIt
    from mdformat.renderer.typing import Postprocess, Render

from ._mdit_plugins.shortcodes import shortcode_plugin
from ._renderer import postprocess_heading, render_fence, render_verbatim, render_zola_shortcode_block

CHANGES_AST: Final = True
RENDERERS: Final[Mapping[str, Render]] = {
    "zola_shortcode": render_verbatim,
    "zola_shortcode_block": render_zola_shortcode_block,
    "fence": render_fence,
}
POSTPROCESSORS: Final[Mapping[str, Postprocess]] = {
    "heading": postprocess_heading,
}


def update_mdit(mdit: MarkdownIt) -> None:
    """Add Zola-specific markdown-it-py plugins."""
    mdit.use(shortcode_plugin)


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
