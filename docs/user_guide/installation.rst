.. _installation:

============
Installation
============

Installation Users
==================

BRiM is currently not available on PyPI. Therefore, you'll need to install the
development version from GitHub using:
```bash
pip install git+https://github.com/TJStienstra/brim.git
```
The optional dependencies can be installed with:
```bash
pip install git+https://github.com/moorepants/BicycleParameters.git
pip install git+https://github.com/TJStienstra/symmeplot.git
```

Installation Developers
=======================

BRiM uses [``poetry``](https://python-poetry.org/) as package manager. To install BRiM
after installing poetry and cloning the repository, run:
```bash
poetry install
```

BRiM offers dependency groups to assist developers:

- ``lint``: packages required for linting.
- ``test``: packages required for testing.
- ``docs``: packages required for building the documentation.

To install optional dependencies from a specific group, run:
```bash
poetry install --with <group>
```

Some of the additional utilities also require extra packages. These can be installed
using:
```bash
poetry install --extras parametrize
poetry install --extras plotting
```

To quickly check code for linting errors, it is recommended to set up ``pre-commit``
hooks by executing:
```bash
pip install pre-commit
pre-commit install
```
