+++
title = "Kitchen Sink"
date = 2024-01-02
weight = 3
+++

Intro paragraph with an inline {{ ref(path="@/other.md") }} shortcode and a [internal link](@/docs/_index.md#anchor).

<!-- more -->

## Diagrams {#diagrams .lead}

A body shortcode whose content must survive byte-for-byte:

{% mermaid() %}
graph TD
  A["node[0]"] --> B[*]
  B --> C{decision}
  C -->|yes| D
  C -->|no| A
{% end %}

## Escaping

To show a shortcode without rendering it, escape it: {{/* youtube(id="x") */}}.

{%/* quote(author="Nobody") */%}
This body is shown literally, *stars* and all.
{%/* end */%}

## Code {#code}

```rust,linenos,linenostart=10,hl_lines=1 3-4,name=main.rs
fn main() {
    println!("hi");
}
```

## Prose features

A table, a footnote[^1], and an alert:

| feature | ok  |
| ------- | --- |
| tables  | yes |

> [!NOTE]
> Zola uses GitHub-flavored alerts.

Term
: Definition body.

[^1]: The footnote text.
