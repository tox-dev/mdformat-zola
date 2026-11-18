"""The installed version of the plugin."""

from __future__ import annotations

__lazy_modules__ = [
    "typing",
]

from importlib.metadata import version
from typing import Final

#: Version of the installed distribution, read from its package metadata.
__version__: Final[str] = version("mdformat-zola")
