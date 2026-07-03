# Contributing to mdformat-zola

Contributions are welcome and appreciated.

## Development setup

Clone the repository and create the development environment:

```bash
git clone https://github.com/gaborbernat/mdformat-zola.git
cd mdformat-zola
tox -e dev
```

This creates a `.tox/dev` virtual environment with all dependencies installed in editable mode.

## Running the checks

Run the tests across the supported Python versions:

```bash
tox -e 3.14,3.13,3.12,3.11
```

Format and lint (ruff, via pre-commit):

```bash
tox -e fix
```

Type check (ty):

```bash
tox -e type
```

The project keeps 100% test coverage and passes ruff and ty on every change.

## How it works

- `_syntax.py` holds the pure, mdformat-independent formatting: it parses shortcode calls, heading attributes, and
  code-fence annotations, and emits their canonical form. `tests/test_syntax.py` covers it in isolation.
- `_mdit_plugins/shortcodes.py` adds the markdown-it-py rules that turn shortcodes into tokens rendered verbatim: an
  inline rule for `{{ … }}` and a block rule that captures `{% … %} … {% end %}` bodies without reflowing them.
- `_renderer.py` renders those tokens, normalizes code-fence annotations, and post-processes heading attributes.
- `_plugin.py` wires everything to mdformat's parser-extension interface.

## Writing tests

Tests format Markdown through the public API and assert on the result:

```python
from __future__ import annotations

import mdformat


def test_example() -> None:
    assert mdformat.text('{{ youtube( id="x" ) }}\n', extensions=["zola"]) == '{{ youtube(id="x") }}\n'
```

Each test checks one behavior; parametrize near-duplicates. Drive the plugin through `mdformat.text`, and cover the pure
helpers in `_syntax.py` through their own tests.

## Pull requests

1. Branch from `main`.
1. Make the change with tests.
1. Run `tox -e fix`, `tox -e type`, and the test environments.
1. Commit following the Commitizen convention and open a pull request.
