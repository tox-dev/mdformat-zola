"""
Parse Zola shortcodes into verbatim tokens so mdformat never reflows or escapes them.

Zola resolves these Tera-like invocations before the Markdown parser runs. Two forms:

- inline ``{{ name(args) }}`` and its escaped form ``{{/* name(args) */}}``
- block ``{% name(args) %}`` ... ``{% end %}`` and its escaped form ``{%/* ... */%}``

The inline rule emits a single ``zola_shortcode`` token; the block rule captures the body verbatim into a
``zola_shortcode_block`` token. The renderer emits both unchanged, so bodies such as Mermaid diagrams stay byte-for-byte
intact.
"""

from __future__ import annotations

__lazy_modules__ = [
    "functools",
]

from functools import partial
from typing import TYPE_CHECKING, Literal, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Callable

    from markdown_it import MarkdownIt
    from markdown_it.rules_block import StateBlock
    from markdown_it.rules_inline import StateInline


def shortcode_plugin(md: MarkdownIt, formatter: Callable[[str], str | None]) -> None:
    # Register the inline and block shortcode rules.
    md.inline.ruler.before("text", "zola_shortcode", partial(_inline_rule, formatter=formatter))
    md.block.ruler.before(
        "fence",
        "zola_shortcode_block",
        partial(_block_rule, formatter=formatter),
        {"alt": ["paragraph", "blockquote", "list"]},
    )


def _inline_rule(
    state: StateInline,
    silent: bool,  # ruff:ignore[boolean-type-hint-positional-argument]  # markdown-it-py callback
    *,
    formatter: Callable[[str], str | None],
) -> bool:
    src, pos = state.src, state.pos
    for open_delim, close_delim, escaped in (("{{/*", "*/}}", True), ("{{", "}}", False)):
        if not src.startswith(open_delim, pos):
            continue
        inner_start = pos + len(open_delim)
        close_pos = _scan_close(src, inner_start, close_delim)
        if close_pos == -1:
            return False
        formatted = formatter(src[inner_start:close_pos])
        if formatted is None:
            return False
        if not silent:
            state.push("zola_shortcode", "", 0).content = _wrap_inline(formatted, escaped=escaped)
        state.pos = close_pos + len(close_delim)
        return True
    return False


def _scan_close(src: str, start: int, close: str) -> int:
    pos = start
    while pos < len(src):
        if (char := src[pos]) in "\"'`":
            nxt = src.find(char, pos + 1)
            if nxt == -1:
                return -1
            pos = nxt + 1
        elif src.startswith(close, pos):
            return pos
        else:
            pos += 1
    return -1


def _wrap_inline(inner: str, *, escaped: bool) -> str:
    return f"{{{{/* {inner} */}}}}" if escaped else f"{{{{ {inner} }}}}"


def _block_rule(
    state: StateBlock,
    start_line: int,
    end_line: int,
    silent: bool,  # ruff:ignore[boolean-type-hint-positional-argument]  # markdown-it-py callback
    *,
    formatter: Callable[[str], str | None],
) -> bool:
    if (opening := _open_delimiter(_line(state, start_line))) is None:
        return False
    escaped, close_delim = opening
    tag_end = start_line
    while not _line(state, tag_end).endswith(close_delim):  # a start tag may span several lines
        tag_end += 1
        if tag_end >= end_line:
            return False
    start = _classify(" ".join(_line(state, line) for line in range(start_line, tag_end + 1)), formatter)
    if start is None or start.kind != "start" or start.escaped != escaped:
        return False
    depth = 1
    line = tag_end
    while line + 1 < end_line:
        line += 1
        if (marker := _classify(_line(state, line), formatter)) is None or marker.escaped != escaped:
            continue
        if marker.kind == "end":
            depth -= 1
            if depth == 0:
                break
        else:
            depth += 1
    else:
        return False
    if silent:
        return True
    token = state.push("zola_shortcode_block", "", 0)
    token.content = state.getLines(tag_end + 1, line, state.blkIndent, keepLastLF=False)
    token.info = start.inner
    token.meta = {"escaped": escaped}
    token.map = [start_line, line]
    state.line = line + 1
    return True


def _open_delimiter(text: str) -> tuple[bool, str] | None:
    if text.startswith("{%/*"):
        return True, "*/%}"
    if text.startswith("{%"):
        return False, "%}"
    return None


def _line(state: StateBlock, line: int) -> str:
    return state.src[state.bMarks[line] + state.tShift[line] : state.eMarks[line]].strip()


def _classify(text: str, formatter: Callable[[str], str | None]) -> _Marker | None:
    for open_delim, close_delim, escaped in (("{%/*", "*/%}", True), ("{%", "%}", False)):
        if not (text.startswith(open_delim) and text.endswith(close_delim)):
            continue
        if len(text) < len(open_delim) + len(close_delim):
            return None
        inner = text[len(open_delim) : -len(close_delim)].strip()
        if inner == "end":
            return _Marker("end", "", escaped)
        if (formatted := formatter(inner)) is not None:
            return _Marker("start", formatted, escaped)
        return None
    return None


class _Marker(NamedTuple):
    # A block-shortcode boundary line: a ``start`` carrying its canonical call, or an ``end``.
    kind: Literal["start", "end"]
    inner: str
    escaped: bool


__all__ = [
    "shortcode_plugin",
]
