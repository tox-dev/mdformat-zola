from __future__ import annotations

from importlib.metadata import version

import mdformat_zola


def test_version() -> None:
    assert mdformat_zola.__version__ == version("mdformat-zola")
