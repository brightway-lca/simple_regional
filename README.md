# simple_regional

[![PyPI](https://img.shields.io/pypi/v/simple_regional.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/simple_regional.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/simple_regional)][pypi status]
[![License](https://img.shields.io/pypi/l/simple_regional)][license]

[![Read the documentation at https://simple_regional.readthedocs.io/](https://img.shields.io/readthedocs/simple_regional/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/simple_regional/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/simple_regional/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/simple_regional/
[read the docs]: https://simple_regional.readthedocs.io/
[tests]: https://github.com/brightway-lca/simple_regional/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/simple_regional
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

**Do not use this library** - it is a dramatic simplification of proper regionalization and will give you incorrect results unless you are very careful.

## Installation

You can install _simple_regional_ via [pip] from PyPI or Anaconda.

## License

Distributed under the terms of the [MIT license][License],
_simple_regional_ is free and open source software.

<!-- github-only -->

[command-line reference]: https://simple_regional.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/simple_regional/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/simple_regional/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/simple_regional/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_simple_regional
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```