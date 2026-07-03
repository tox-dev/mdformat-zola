"""Renderers for Zola Markdown elements."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Final

from mdformat_zola._syntax import format_attrs, format_fence_info

if TYPE_CHECKING:
    from mdformat.renderer import RenderContext, RenderTreeNode

LOGGER: Final = logging.getLogger(__name__)
_HEADING_ATTRS: Final = re.compile(r"^(?P<text>.*?)[ \t]*\{(?P<attrs>[^{}]*)\}[ \t]*$")


def render_verbatim(node: RenderTreeNode, _context: RenderContext) -> str:
    """Render a shortcode token exactly as captured, without escaping or wrapping."""
    return node.content


def render_fence(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a code fence, normalizing Zola annotations and running any code formatter."""
    info = format_fence_info(node.info)
    lang = info.split(",", 1)[0] if info else ""
    code_block = node.content

    fence_char = "~" if "`" in info else "`"

    if fmt_func := context.options.get("codeformatters", {}).get(lang):
        try:
            code_block = fmt_func(code_block, info)
        except Exception:  # noqa: BLE001 - a formatter error must never crash mdformat
            LOGGER.warning("Failed formatting content of a %s code block", lang)
        else:
            if code_block and not code_block.endswith("\n"):
                code_block += "\n"

    fence = fence_char * max(3, _longest_consecutive_sequence(code_block, fence_char) + 1)
    return f"{fence}{info}\n{code_block}{fence}"


def postprocess_heading(text: str, _node: RenderTreeNode, _context: RenderContext) -> str:
    """Normalize a trailing ``{#id .class}`` attribute block on a rendered heading."""
    match = _HEADING_ATTRS.match(text)
    if match is None:
        return text
    attrs = format_attrs(match["attrs"])
    if attrs is None:
        return text
    return f"{match['text']} {{{attrs}}}"


def _longest_consecutive_sequence(text: str, char: str) -> int:
    longest = current = 0
    for candidate in text:
        current = current + 1 if candidate == char else 0
        longest = max(longest, current)
    return longest


__all__ = [
    "postprocess_heading",
    "render_fence",
    "render_verbatim",
]
