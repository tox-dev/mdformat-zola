# Contributing to mdformat-zola

## Development setup

Clone the repository and create the development environment:

```bash
git clone https://github.com/tox-dev/mdformat-zola.git
cd mdformat-zola
tox -e dev
```

This creates a `.tox/dev` virtual environment with all dependencies installed in editable mode.

## Running the checks

Run the tests across the supported Python versions:

```bash
tox -e 3.15,3.14,3.13,3.12,3.11
```

Format and lint through the configured tox task:

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
- `_mdit_plugins/shortcodes.py` adds the markdown-it-py rules that turn shortcodes into tokens: an inline rule for
  `{{ … }}` and a block rule that captures `{% … %} … {% end %}` bodies.
- `_renderer.py` renders those tokens, formats prose-shortcode bodies as Markdown while leaving raw ones (Mermaid and
  the like) verbatim, normalizes code-fence annotations, and post-processes heading attributes.
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

Add a `changelog.d/+short-name.<type>.md` fragment when a pull request changes what package users can use or observe.
Use one fragment per user-facing change. The release workflow links each fragment to its merged squash pull request.

| Type          | Changelog section | Use for                                                    |
| ------------- | ----------------- | ---------------------------------------------------------- |
| `feature`     | Added             | New capabilities and Python support additions or removals  |
| `change`      | Changes           | Changed behavior that remains available                    |
| `bugfix`      | Fixed             | Corrected behavior                                         |
| `doc`         | Documentation     | Documentation changes users need to know about             |
| `breaking`    | Breaking changes  | Changes that require users to update code or configuration |
| `security`    | Security          | Security fixes users need to act on                        |
| `performance` | Performance       | User-visible speed or resource improvements                |
| `deprecation` | Deprecated        | Supported behavior scheduled for removal                   |
| `removal`     | Removed           | Removed user-facing capabilities other than Python support |
| `packaging`   | Packaging         | Install, wheel, or distribution changes                    |

Use `skip news` for a pull request with no user-facing change. The label can be applied after the pull request opens. A
fragment still has to be valid when the label is present. Dependabot, pre-commit.ci, and repository automation receive
the label when their pull request has no fragment.

The release workflow credits the pull request author. If several people authored the change, add their linked GitHub
handles in one `by` phrase in the fragment. Omit bots and reviewers.

1. Branch from `main`.
1. Make the change with tests.
1. Add a changelog fragment for a user-facing change, or apply `skip news` for internal maintenance.
1. Run `tox -e fix`, `tox -e type`, and the test environments.
1. Commit following the Commitizen convention and open a pull request.

## Make a release

Run **Prepare release** on `main`. `auto` chooses a major version for a `breaking` fragment, a minor version for a
`feature` fragment, and a patch version for other user-facing categories. The workflow formats the assembled
`CHANGELOG.md` with `prek` before the repository App pushes the release commit and tag. The tag workflow publishes to
PyPI through trusted publishing, then creates the GitHub Release from the tagged changelog.
