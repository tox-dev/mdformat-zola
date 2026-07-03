from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import mdformat
import mdformat.plugins
import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

# Every installed extension, matching how the mdformat CLI runs on a real Zola site.
_EXTENSIONS: Final = sorted(mdformat.plugins.PARSER_EXTENSIONS)


@pytest.fixture
def fmt() -> Callable[..., str]:
    def format_markdown(
        text: str,
        *,
        wrap: int | str = 120,
        codeformatters: Sequence[str] = (),
        plugin: Mapping[str, Any] | None = None,
    ) -> str:
        options: dict[str, Any] = {"wrap": wrap}
        if plugin is not None:
            options["plugin"] = {"zola": plugin}
        return mdformat.text(text, options=options, extensions=_EXTENSIONS, codeformatters=codeformatters)

    return format_markdown
