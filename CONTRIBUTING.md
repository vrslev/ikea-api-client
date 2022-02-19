# Contributing

## Setting up development environment

This package uses [poetry](https://python-poetry.org) for everything, install it if you don't have it:

```bash
pip install poetry
```

After cloning the repository, run:

```bash
poetry install --extras all
```

This will install all optional and dev dependencies, they're required for development.

### Running tests

```bash
pytest
```

### Setting up git hooks

We use `pre-commit`. To install it, run this after [activating virtual environment](https://python-poetry.org/docs/basic-usage#activating-the-virtual-environment):

```bash
pre-commit install
```

Now before any commit you make, changes will be validated, files reformatted etc.

### Setting up type checker

This project uses [pyright](https://github.com/microsoft/pyright) for [type checking](https://www.python.org/dev/peps/pep-0484/). It is an npm package, so if you don't have Node, don't bother installing — you will see issues that come up in continuous integration on PR. If you use VS Code, Pyright is built-in.

To install _pyright_, run:

```bash
npm install -g pyright
```
