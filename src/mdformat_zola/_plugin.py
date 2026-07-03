"""Mdformat plugin interface for Zola markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

    from markdown_it import MarkdownIt
    from mdformat.renderer.typing import Postprocess, Render

from ._mdit_plugins.shortcodes import shortcode_plugin
from ._renderer import postprocess_heading, render_fence, render_verbatim

CHANGES_AST: Final = True
RENDERERS: Final[Mapping[str, Render]] = {
    "zola_shortcode": render_verbatim,
    "zola_shortcode_block": render_verbatim,
    "fence": render_fence,
}
POSTPROCESSORS: Final[Mapping[str, Postprocess]] = {
    "heading": postprocess_heading,
}


def update_mdit(mdit: MarkdownIt) -> None:
    """Add Zola-specific markdown-it-py plugins."""
    mdit.use(shortcode_plugin)


__all__ = [
    "CHANGES_AST",
    "POSTPROCESSORS",
    "RENDERERS",
    "update_mdit",
]
