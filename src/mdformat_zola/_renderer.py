"""Renderers for Zola Markdown elements."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Final

import mdformat
import mdformat.plugins

from mdformat_zola._syntax import format_attrs, format_fence_info

if TYPE_CHECKING:
    from mdformat.renderer import RenderContext, RenderTreeNode

LOGGER: Final = logging.getLogger(__name__)
_HEADING_ATTRS: Final = re.compile(r"^(?P<text>.*?)[ \t]*\{(?P<attrs>[^{}]*)\}[ \t]*$")

# Shortcodes whose body is Markdown that Zola re-renders (as opposed to raw text like a Mermaid diagram). Their bodies
# are formatted recursively by default; a Zola site can override the set via the `markdown_shortcodes` plugin option.
_DEFAULT_MARKDOWN_SHORTCODES: Final = frozenset({
    "admonition",
    "aside",
    "callout",
    "caution",
    "details",
    "important",
    "note",
    "quote",
    "tip",
    "warning",
})


def render_verbatim(node: RenderTreeNode, _context: RenderContext) -> str:
    """Render an inline shortcode token exactly as captured, without escaping or wrapping."""
    return node.content


def render_zola_shortcode_block(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a body shortcode, formatting the body as Markdown for known prose shortcodes."""
    inner, escaped, body = node.info, node.meta["escaped"], node.content
    name = inner.split("(", 1)[0]
    if body and not escaped and name in _markdown_shortcodes(context):
        body = _format_markdown_body(body, context)
    open_delim, close_delim, end_tag = ("{%/*", "*/%}", "{%/* end */%}") if escaped else ("{%", "%}", "{% end %}")
    start_tag = f"{open_delim} {inner} {close_delim}"
    return f"{start_tag}\n{body}\n{end_tag}" if body else f"{start_tag}\n{end_tag}"


def _markdown_shortcodes(context: RenderContext) -> frozenset[str]:
    configured = context.options.get("mdformat", {}).get("plugin", {}).get("zola", {}).get("markdown_shortcodes")
    if configured is None:
        return _DEFAULT_MARKDOWN_SHORTCODES
    if isinstance(configured, str):
        configured = configured.split(",")
    return frozenset(name.strip() for name in configured if name.strip())


def _format_markdown_body(body: str, context: RenderContext) -> str:
    names = {plugin: name for name, plugin in mdformat.plugins.PARSER_EXTENSIONS.items()}
    extensions = [names[plugin] for plugin in context.options.get("parser_extension", [])]
    return mdformat.text(
        body,
        options=context.options.get("mdformat", {}),
        extensions=extensions,
        codeformatters=list(context.options.get("codeformatters", {})),
    ).rstrip("\n")


def render_fence(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a code fence, normalizing Zola annotations and running any code formatter."""
    info = format_fence_info(node.info)
    lang = info.split(",", 1)[0]
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


def _longest_consecutive_sequence(text: str, char: str) -> int:
    longest = current = 0
    for candidate in text:
        current = current + 1 if candidate == char else 0
        longest = max(longest, current)
    return longest


def postprocess_heading(text: str, _node: RenderTreeNode, _context: RenderContext) -> str:
    """Normalize a trailing ``{#id .class}`` attribute block on a rendered heading."""
    match = _HEADING_ATTRS.match(text)
    if match is None:
        return text
    attrs = format_attrs(match["attrs"])
    if attrs is None:
        return text
    return f"{match['text']} {{{attrs}}}"


__all__ = [
    "postprocess_heading",
    "render_fence",
    "render_verbatim",
    "render_zola_shortcode_block",
]
