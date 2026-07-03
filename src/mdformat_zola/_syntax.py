"""
Canonical formatting for Zola-specific Markdown constructs.

Pure functions with no ``mdformat``/``markdown-it`` coupling so they can be unit tested in isolation. They cover the
three Zola constructs where ordering carries no meaning, so we impose a single stable order:

- shortcode calls ``name(kwargs)`` -- keyword arguments sorted by name
- heading attributes ``{#id .class key=value}`` -- id, then sorted classes, then sorted pairs
- code-fence annotations ``lang,linenos,hl_lines=...`` -- fixed annotation order

The shortcode grammar mirrors Zola's ``components/markdown/src/content.pest``.
"""

from __future__ import annotations

import re
import string
from typing import Final

_IDENT: Final = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMBER: Final = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")
_IDENT_CHARS: Final = frozenset(string.ascii_letters + string.digits + "_")
_QUOTES: Final = "\"'`"
_WHITESPACE: Final = " \t\r\n"
_ATTR_TOKEN: Final = re.compile(
    r"[ \t]*(?:"
    r"\.(?P<cls>[^\s.#={}]+)"
    r"|#(?P<id>[^\s.#={}]+)"
    r"|(?P<key>[A-Za-z_][A-Za-z0-9_-]*)=(?P<val>\"[^\"]*\"|'[^']*'|[^\s{}]+)"
    r")[ \t]*"
)
_FENCE_ORDER: Final = ("linenos", "linenostart", "hl_lines", "hide_lines", "name")


class _ParseError(Exception):
    """Raised when a shortcode invocation does not match Zola's grammar."""


def format_shortcode(inner: str) -> str | None:
    """
    Return the canonical form of a shortcode invocation, or ``None`` if invalid.

    ``inner`` is the text between the delimiters, e.g. ``youtube(id="x", autoplay=true)``. Sorts keyword arguments by
    name. Returns ``None`` for an invalid call so the caller leaves the source untouched, as Zola itself renders an
    invalid shortcode verbatim.
    """
    try:
        name, args = _parse_call(inner)
    except _ParseError:
        return None
    body = ", ".join(f"{key}={value}" for key, value in sorted(args))
    return f"{name}({body})"


def format_attrs(inner: str) -> str | None:
    """
    Return canonical heading attributes, or ``None`` if not a valid attribute block.

    ``inner`` is the text between the braces. Orders the id first, then classes and key-value pairs, each sorted.
    Returns ``None`` for anything that is not a pure attribute block, so a trailing inline shortcode stays untouched.
    """
    if not inner.strip():
        return None
    ids: list[str] = []
    classes: list[str] = []
    pairs: list[tuple[str, str]] = []
    pos = 0
    while pos < len(inner):
        match = _ATTR_TOKEN.match(inner, pos)
        if match is None or match.end() == pos:
            return None
        if cls := match.group("cls"):
            classes.append(cls)
        elif ident := match.group("id"):
            ids.append(ident)
        else:
            pairs.append((match.group("key"), _format_attr_value(match.group("val"))))
        pos = match.end()
    parts = [f"#{i}" for i in sorted(ids)] + [f".{c}" for c in sorted(classes)] + [f"{k}={v}" for k, v in sorted(pairs)]
    return " ".join(parts)


def format_fence_info(info: str) -> str:
    """
    Return the canonical code-fence info string.

    Keeps the language first, reorders known Zola annotations to :data:`_FENCE_ORDER`, normalizes their whitespace, and
    appends any unknown annotation in its original order.
    """
    info = info.strip()
    if "," not in info:
        return info
    lang, *rest = info.split(",")
    known: dict[str, str] = {}
    unknown: list[str] = []
    for raw in rest:
        if not (annotation := raw.strip()):
            continue
        key = annotation.split("=", 1)[0].strip()
        if key in _FENCE_ORDER and key not in known:
            known[key] = _format_annotation(key, annotation)
        else:
            unknown.append(annotation)
    ordered = [known[k] for k in _FENCE_ORDER if k in known] + unknown
    return ",".join([lang.strip(), *ordered])


def _parse_call(inner: str) -> tuple[str, list[tuple[str, str]]]:
    pos = _skip_ws(inner, 0)
    if not (name := _IDENT.match(inner, pos)):
        raise _ParseError
    pos = _skip_ws(inner, name.end())
    if pos >= len(inner) or inner[pos] != "(":
        raise _ParseError
    pos = _skip_ws(inner, pos + 1)
    if pos < len(inner) and inner[pos] == ")":
        args: list[tuple[str, str]] = []
        pos += 1
    else:
        args, pos = _parse_args(inner, pos)
    if _skip_ws(inner, pos) != len(inner):
        raise _ParseError
    return name.group(), args


def _parse_args(inner: str, pos: int) -> tuple[list[tuple[str, str]], int]:
    args: list[tuple[str, str]] = []
    while True:
        if not (key := _IDENT.match(inner, pos)):
            raise _ParseError
        pos = _skip_ws(inner, key.end())
        if pos >= len(inner) or inner[pos] != "=":
            raise _ParseError
        value, pos = _parse_value(inner, pos + 1)
        args.append((key.group(), value))
        pos = _skip_ws(inner, pos)
        if pos >= len(inner):
            raise _ParseError
        if inner[pos] == ")":
            return args, pos + 1
        if inner[pos] != ",":
            raise _ParseError
        pos = _skip_ws(inner, pos + 1)


def _parse_value(source: str, pos: int) -> tuple[str, int]:
    pos = _skip_ws(source, pos)
    if pos >= len(source):
        raise _ParseError
    char = source[pos]
    if char in _QUOTES:
        return _parse_string(source, pos)
    if char == "[":
        return _parse_array(source, pos)
    for literal in ("true", "false"):
        end = pos + len(literal)
        if source.startswith(literal, pos) and (end >= len(source) or source[end] not in _IDENT_CHARS):
            return literal, end
    if match := _NUMBER.match(source, pos):
        return match.group(), match.end()
    raise _ParseError


def _parse_string(source: str, pos: int) -> tuple[str, int]:
    quote = source[pos]
    end = source.find(quote, pos + 1)
    if end == -1:
        raise _ParseError
    return _format_string(source[pos + 1 : end]), end + 1


def _parse_array(source: str, pos: int) -> tuple[str, int]:
    pos = _skip_ws(source, pos + 1)
    if pos < len(source) and source[pos] == "]":
        return "[]", pos + 1
    elements: list[str] = []
    while True:
        value, pos = _parse_value(source, pos)
        elements.append(value)
        pos = _skip_ws(source, pos)
        if pos >= len(source):
            raise _ParseError
        if source[pos] == "]":
            return "[" + ", ".join(elements) + "]", pos + 1
        if source[pos] != ",":
            raise _ParseError
        pos = _skip_ws(source, pos + 1)
        if pos < len(source) and source[pos] == "]":
            return "[" + ", ".join(elements) + "]", pos + 1


def _format_string(value: str) -> str:
    delimiter = next(quote for quote in _QUOTES if quote not in value)
    return f"{delimiter}{value}{delimiter}"


def _format_attr_value(raw: str) -> str:
    value = raw[1:-1] if raw[0] in "\"'" else raw
    return f'"{value}"' if " " in value or "=" in value else value


def _format_annotation(key: str, annotation: str) -> str:
    if key == "linenos":
        return "linenos"
    value = annotation.partition("=")[2].strip()
    if key in {"hl_lines", "hide_lines"}:
        value = " ".join(value.split())
    return f"{key}={value}"


def _skip_ws(source: str, pos: int) -> int:
    while pos < len(source) and source[pos] in _WHITESPACE:
        pos += 1
    return pos


__all__ = [
    "format_attrs",
    "format_fence_info",
    "format_shortcode",
]
