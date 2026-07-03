"""Mdformat plugin for Zola-flavored Markdown."""

from __future__ import annotations

from importlib.metadata import version

__version__ = version("mdformat-zola")

from ._plugin import CHANGES_AST, POSTPROCESSORS, RENDERERS, add_cli_argument_group, update_mdit

__all__ = [
    "CHANGES_AST",
    "POSTPROCESSORS",
    "RENDERERS",
    "__version__",
    "add_cli_argument_group",
    "update_mdit",
]
