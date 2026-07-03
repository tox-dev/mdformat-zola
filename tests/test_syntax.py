from __future__ import annotations

import pytest

from mdformat_zola._syntax import format_attrs, format_fence_info, format_shortcode


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param('youtube(id="x")', 'youtube(id="x")', id="simple"),
        pytest.param("basic()", "basic()", id="no_args"),
        pytest.param("f(b=2, a=1)", "f(a=1, b=2)", id="sorted"),
        pytest.param("  f (  a = 1  )  ", "f(a=1)", id="whitespace_collapsed"),
        pytest.param("f(a=true, b=false)", "f(a=true, b=false)", id="booleans"),
        pytest.param("f(a=3, b=-2, c=1.5, d=-0.5)", "f(a=3, b=-2, c=1.5, d=-0.5)", id="numbers"),
        pytest.param("f(a='x')", 'f(a="x")', id="single_to_double_quote"),
        pytest.param("f(a='say \"hi\"')", "f(a='say \"hi\"')", id="keep_single_when_double_inside"),
        pytest.param("f(a=`has \"d\" and 'q'`)", "f(a=`has \"d\" and 'q'`)", id="backtick_when_both_inside"),
        pytest.param("f(a=[3, 1, 2])", "f(a=[3, 1, 2])", id="array_order_preserved"),
        pytest.param("f(a=[])", "f(a=[])", id="empty_array"),
        pytest.param('f(a=[1, "x", true])', 'f(a=[1, "x", true])', id="mixed_array"),
        pytest.param("f(a=[1, 2,])", "f(a=[1, 2])", id="array_trailing_comma"),
    ],
)
def test_format_shortcode_valid(text: str, expected: str) -> None:
    assert format_shortcode(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("not a shortcode", id="prose"),
        pytest.param("foo", id="no_parens"),
        pytest.param("foo(", id="unclosed_parens"),
        pytest.param("foo(a=true", id="value_at_end"),
        pytest.param("foo(a)", id="key_without_value"),
        pytest.param("foo(a=)", id="value_missing"),
        pytest.param("foo(a=1", id="unterminated_args"),
        pytest.param("foo(a=1,)", id="trailing_comma_kwarg"),
        pytest.param("foo(a=1 b=2)", id="missing_comma"),
        pytest.param("foo(a=@)", id="bad_value"),
        pytest.param('foo(a="x)', id="unterminated_string"),
        pytest.param("foo(a=[1)", id="unterminated_array"),
        pytest.param("foo(a=[1 2])", id="array_missing_comma"),
        pytest.param("foo(a=[1,", id="array_unterminated_after_comma"),
        pytest.param("foo(a=[1", id="array_unterminated_after_element"),
        pytest.param("foo()x", id="trailing_garbage"),
        pytest.param("123()", id="numeric_name"),
    ],
)
def test_format_shortcode_invalid(text: str) -> None:
    assert format_shortcode(text) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("#x", "#x", id="id"),
        pytest.param(".a", ".a", id="class"),
        pytest.param("k=v", "k=v", id="pair"),
        pytest.param('k="a b"', 'k="a b"', id="quoted_space_value"),
        pytest.param("k='a b'", 'k="a b"', id="single_quoted_normalized"),
        pytest.param('k="a=b"', 'k="a=b"', id="value_with_equals"),
        pytest.param(".z .a #id b=2 a=1", "#id .a .z a=1 b=2", id="full_sorted"),
        pytest.param("  #id   .a  ", "#id .a", id="whitespace"),
    ],
)
def test_format_attrs_valid(text: str, expected: str) -> None:
    assert format_attrs(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace_only"),
        pytest.param("invalid", id="bare_word"),
        pytest.param("icon()", id="looks_like_shortcode"),
    ],
)
def test_format_attrs_invalid(text: str) -> None:
    assert format_attrs(text) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("python", "python", id="no_annotations"),
        pytest.param("rust,linenos", "rust,linenos", id="single_flag"),
        pytest.param(
            "rust, hl_lines=3-4  8-9 ,linenos , linenostart=10 ,name=mod.rs",
            "rust,linenos,linenostart=10,hl_lines=3-4 8-9,name=mod.rs",
            id="reordered",
        ),
        pytest.param("rust,linenos=table", "rust,linenos", id="linenos_ignores_value"),
        pytest.param("rust,foo,bar=1", "rust,foo,bar=1", id="unknown_preserved"),
        pytest.param("rust,linenos,linenos", "rust,linenos,linenos", id="duplicate_known"),
        pytest.param("rust,,linenos", "rust,linenos", id="empty_annotation_skipped"),
        pytest.param("  rust , linenos ", "rust,linenos", id="lang_stripped"),
    ],
)
def test_format_fence_info(text: str, expected: str) -> None:
    assert format_fence_info(text) == expected
