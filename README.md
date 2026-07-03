# mdformat-zola

[![PyPI](https://img.shields.io/pypi/v/mdformat-zola?style=flat-square)](https://pypi.org/project/mdformat-zola/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/mdformat-zola.svg)](https://pypi.org/project/mdformat-zola/)
[![check](https://github.com/gaborbernat/mdformat-zola/actions/workflows/check.yaml/badge.svg)](https://github.com/gaborbernat/mdformat-zola/actions/workflows/check.yaml)

Mdformat plugin for [Zola](https://www.getzola.org)-flavored Markdown. It formats Zola content files while keeping
shortcodes, heading anchors, and code-block annotations intact.

Plain mdformat mangles Zola content. It reflows shortcode bodies (a Mermaid diagram becomes one escaped line), escapes
the `*` in `{{/* … */}}`, and wraps long inline shortcodes mid-call. This plugin adds Zola's syntax to mdformat so those
constructs round-trip.

## Zola syntax

Each construct below gets one stable form. Where Zola treats ordering as insignificant, the plugin sorts.

### Shortcodes

The plugin normalizes inline shortcodes `{{ name(args) }}` and their escaped form `{{/* name(args) */}}`: it collapses
whitespace, sorts arguments by name, and settles on one quote style. It does not wrap or escape them.

**Input:**

```markdown
{{  youtube( autoplay=true ,  id="dQw4w9WgXcQ" ) }}
```

**Output:**

```markdown
{{ youtube(autoplay=true, id="dQw4w9WgXcQ") }}
```

Body shortcodes `{% name(args) %} … {% end %}` (and the escaped `{%/* … */%}`) get the same treatment on their opening
tag. A raw body such as a Mermaid diagram stays byte-for-byte:

```markdown
{% mermaid() %}
graph TD
  A["velodex[x]"] --> B[*]
{% end %}
```

The body of a prose shortcode is Markdown that Zola re-renders, so the plugin formats it. By default this applies to
`admonition`, `aside`, `callout`, `caution`, `details`, `important`, `note`, `quote`, `tip`, and `warning`; every other
shortcode keeps its body verbatim. Point the plugin at your own set with the `markdown_shortcodes` option, on the CLI or
in `.mdformat.toml`:

```bash
mdformat --zola-markdown-shortcodes quote,note,sidebar content/
```

```toml
# .mdformat.toml
[plugin.zola]
markdown_shortcodes = ["quote", "note", "sidebar"]
```

Pass an empty value to keep every body verbatim.

### Heading anchors

Zola lets you pin a heading's [id and classes](https://www.getzola.org/documentation/content/linking/) with a
`{#id .class}` suffix. The plugin puts the id first, then the classes in alphabetical order:

```markdown
## Introduction {.lead #intro}
```

Formats to:

```markdown
## Introduction {#intro .lead}
```

### Code-block annotations

The plugin reorders Zola's
[syntax-highlighting annotations](https://www.getzola.org/documentation/content/syntax-highlighting/) to a fixed
sequence (`linenos`, `linenostart`, `hl_lines`, `hide_lines`, `name`), normalizes their whitespace, and keeps unknown
annotations:

````markdown
```rust, hl_lines=3-4  8-9,linenos , linenostart=10
````

Formats to:

````markdown
```rust,linenos,linenostart=10,hl_lines=3-4 8-9
````

Internal links such as `[text](@/pages/about.md#anchor)` survive as ordinary links, no special handling needed.

## Bundled features

Installing the plugin pulls in the mdformat plugins that cover the rest of Zola's Markdown flavor (GitHub-Flavored
Markdown with footnotes, definition lists, alerts, and TOML `+++` frontmatter), plus code formatters for fenced blocks:

**Markdown syntax:**

- [mdformat-gfm](https://github.com/hukkin/mdformat-gfm) - tables, strikethrough, task lists, autolinks
- [mdformat-front-matters](https://github.com/kyleking/mdformat-front-matters) - TOML/YAML/JSON frontmatter
- [mdformat-gfm-alerts](https://github.com/KyleKing/mdformat-gfm-alerts) - blockquote alerts (`[!NOTE]`, `[!WARNING]`)
- [mdformat-footnote](https://github.com/executablebooks/mdformat-footnote) - footnotes
- [mdformat-deflist](https://github.com/executablebooks/mdformat-deflist) - definition lists

**Code-block formatting:**

- [mdformat-ruff](https://github.com/Freed-Wu/mdformat-ruff) - Python blocks with ruff
- [mdformat-shfmt](https://github.com/hukkin/mdformat-shfmt) - shell blocks with shfmt
- [mdformat-config](https://github.com/hukkin/mdformat-config) - JSON, YAML, TOML blocks
- [mdformat-web](https://github.com/hukkin/mdformat-web) - HTML, CSS, JavaScript blocks
- [mdformat-pyproject](https://github.com/csala/mdformat-pyproject) - pyproject.toml blocks

## Usage

```bash
mdformat content/
```
