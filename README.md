# BRiM
A Modular and Extensible Open-Source Framework for Creating Bicycle-Rider Models.

This package is still under development, therefore there is no guarantee on backward
compatibility.

## Installation
`BRiM` is currently not available on `PyPI`. Therefore, you'll need to install the
development version from GitHub using:
```bash
pip install git+https://github.com/TJStienstra/brim.git
```
The optional dependencies can be installed with:
```bash
pip install git+https://github.com/moorepants/BicycleParameters.git
pip install git+https://github.com/TJStienstra/symmeplot.git
```

## Contributing
One of the aims when developing this package make it easier for researchers to also
share their bicycle-rider models for research dissemination and academic
reproducibility. This goal is aided as follows. [`poetry`](https://python-poetry.org/)
is used to manage the dependencies. After installing `poetry` one can install the
necessary dependencies for developing using:
```bash
poetry install
```
### Testing
[`pytest`](https://docs.pytest.org) is used for testing. To make sure that each feature
introduced in `brim` is tested, we have set the code coverage to 100%. If a function
should for some reason not be tested, then it should be ignored instead of reducing the
obligated coverage percentage. Hint: if you like to have nice formatting when running
`pytest` you can also install [`pytest-sugar`](https://github.com/Teemu/pytest-sugar).
You can run the tests using:
```bash
pytest --cov
```

### Linting
To make sure that the same code style is used among different contributors, there has
been chosen to set up [`ruff`](https://beta.ruff.rs). `ruff` is a fast Python linter,
which makes sure that everyone uses for example the same spacing and writes some
documentation for new features. Besides `ruff` we did decide to use type hinting in the
function descriptions, but not within the functions. `mypy` has also been removed as it
was mainly causing problems. To run `ruff` use:
```bash
ruff .
```
With `pre-commit` it is also possible to have some of the checks automatically done on
committing a change. This can be set up by running the following:
```bash
pip install pre-commit
pre-commit install
```

### Documentation
While you can trigger a build of the documentation manually using:
```bash
docs/make.bat html
```
It is also possible to have the documentation automatically build when a change is
committed. This can be set up by running the following:
```bash
pip install sphinx-autobuild
```
and then running:
```bash
sphinx-autobuild docs docs/_build/html
```

A lot of the above settings are inspired by [Hypermodern Python][1] by Claudio Jolowicz
and [Setting up Python Projects][2] by Johannes Schmidt. A tutorial by Aahil Mehta was
followed to set up the documenation: [Sphinx Tutorial][3].

[1]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/
[2]: https://johschmidt42.medium.com/setting-up-python-projects-part-i-408603868c08
[3]: https://www.aahilm.com/blog/documenting-large-projects-with-sphinx
