# BRiM
A Modular and Extensible Open-Source Framework for Creating Bicycle-Rider Models

## Installation
This packages has not been released yet.

## Contributing
One of the aims when developing this package make it more easy for researchers to also
share their bicycle-rider models for research dissemination and academic
reproducibility. This goal is aided as follows. [`poetry`](https://python-poetry.org/)
is used to manage the dependencies. After installing `poetry` one can install the
necessary dependencies for developing using:
```
poetry install
```
[`pytest`](https://docs.pytest.org) is used for testing. To make sure that each feature
introduced in `brim` is tested, we have set the code coverage to 100%. If a function
should for some reason not be tested, then it should be ignored instead of reducing the
obligated coverage percentage. Hint: if you like to have nice formatting when running
`pytest` you can also install [`pytest-sugar`](https://github.com/Teemu/pytest-sugar).

To make sure that the same code style is used among different contributors, there has
been chosen to set up [`ruff`](https://beta.ruff.rs). `ruff` is a fast Python linter,
which makes sure that everyone uses for example the same spacing and writes some
documentation for new features. Besides `ruff` we have also chosen to use `mypy` for the
type checking. If a variable is however too difficult to type feel free to use `Any`.
With `pre-commit` it is also possible to have some of the checks automatically done on
committing a change. This can be set up by running the following:
```
pip install pre-commit
pre-commit install
```

While an option would be to use [`nox`](https://nox.thea.codes) to run all these tests.
It has currently not been set up. Before committing any changes it is advised to run the
following commands:
```
ruff .
pytest --cov
```
Possibly one can also build the documentation, to check for any errors using:
```
TODO
```

A lot of the above settings are inspired by [Hypermodern Python][1] by Claudio Jolowicz
and [Setting up Python Projects][2] by Johannes Schmidt.

[1]: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/
[2]: https://johschmidt42.medium.com/setting-up-python-projects-part-i-408603868c08
