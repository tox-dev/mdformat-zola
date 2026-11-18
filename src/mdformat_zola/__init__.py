"""Mdformat plugin for Zola-flavored Markdown."""

from __future__ import annotations

__lazy_modules__ = [
    f"{__spec__.parent}._plugin",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
    f"{__spec__.parent}._version",  # ty: ignore[missing-union-attribute]  # imported modules have a spec
]

from ._plugin import CHANGES_AST, POSTPROCESSORS, RENDERERS, add_cli_argument_group, update_mdit
from ._version import __version__

__all__ = [
    "CHANGES_AST",
    "POSTPROCESSORS",
    "RENDERERS",
    "__version__",
    "add_cli_argument_group",
    "update_mdit",
]
