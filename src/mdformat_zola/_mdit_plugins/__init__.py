"""Zola markdown-it-py plugins."""

from __future__ import annotations

__lazy_modules__ = [
    f"{__spec__.parent}.shortcodes",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

from .shortcodes import shortcode_plugin

__all__ = [
    "shortcode_plugin",
]
