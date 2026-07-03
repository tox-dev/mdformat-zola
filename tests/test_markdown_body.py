from __future__ import annotations

import argparse
from textwrap import dedent
from typing import TYPE_CHECKING, Final

import pytest

from mdformat_zola import add_cli_argument_group

if TYPE_CHECKING:
    from collections.abc import Callable

_LONG: Final = " ".join(["word"] * 40)


def test_markdown_body_formatted_by_default(fmt: Callable[..., str]) -> None:
    body = fmt(f"{{% note() %}}\n{_LONG}\n{{% end %}}\n").splitlines()[1:-1]
    assert len(body) > 1  # the long line got wrapped, so the body is Markdown-formatted
    assert all(len(line) <= 120 for line in body)


def test_markdown_body_normalizes_content(fmt: Callable[..., str]) -> None:
    start = '{% quote(author="X") %}\ntext   with    extra     spaces\n{% end %}\n'
    assert fmt(start) == '{% quote(author="X") %}\ntext with extra spaces\n{% end %}\n'


@pytest.mark.parametrize("name", ["mermaid", "katex", "chart", "custom_raw"])
def test_non_prose_shortcode_body_verbatim(fmt: Callable[..., str], name: str) -> None:
    start = f"{{% {name}() %}}\n{_LONG}\n{{% end %}}\n"
    assert fmt(start) == start


def test_escaped_prose_shortcode_body_verbatim(fmt: Callable[..., str]) -> None:
    start = f"{{%/* note() */%}}\n{_LONG}\n{{%/* end */%}}\n"
    assert fmt(start) == start


def test_config_disables_all_body_formatting(fmt: Callable[..., str]) -> None:
    start = f"{{% note() %}}\n{_LONG}\n{{% end %}}\n"
    assert fmt(start, plugin={"markdown_shortcodes": ""}) == start


def test_config_string_replaces_default_set(fmt: Callable[..., str]) -> None:
    note = f"{{% note() %}}\n{_LONG}\n{{% end %}}\n"
    assert fmt(note, plugin={"markdown_shortcodes": "sidebar,quote"}) == note  # note dropped, so verbatim
    sidebar = f"{{% sidebar() %}}\n{_LONG}\n{{% end %}}\n"
    assert len(fmt(sidebar, plugin={"markdown_shortcodes": "sidebar,quote"}).splitlines()) > 3  # sidebar formatted


def test_config_list_form(fmt: Callable[..., str]) -> None:
    start = f"{{% aside() %}}\n{_LONG}\n{{% end %}}\n"
    out = fmt(start, plugin={"markdown_shortcodes": ["aside"]})
    assert out.splitlines()[0] == "{% aside() %}"
    assert len(out.splitlines()) > 3


def test_nested_prose_body_formatted_recursively(fmt: Callable[..., str]) -> None:
    start = dedent(f"""\
        {{% note() %}}
        outer intro

        {{% quote() %}}
        {_LONG}
        {{% end %}}
        {{% end %}}
        """)
    out = fmt(start)
    assert "{% note() %}" in out
    assert "{% quote() %}" in out
    assert all(len(line) <= 120 for line in out.splitlines())  # the inner body was wrapped, not left verbatim
    assert fmt(out) == out


def test_cli_argument_registered() -> None:
    parser = argparse.ArgumentParser()
    add_cli_argument_group(parser.add_argument_group("zola"))
    namespace = parser.parse_args(["--zola-markdown-shortcodes", "quote,note"])
    assert getattr(namespace, "plugin.zola.markdown_shortcodes") == "quote,note"


def test_cli_argument_suppressed_when_unset() -> None:
    parser = argparse.ArgumentParser()
    add_cli_argument_group(parser.add_argument_group("zola"))
    assert not hasattr(parser.parse_args([]), "plugin.zola.markdown_shortcodes")
