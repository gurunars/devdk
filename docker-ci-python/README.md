# docker-ci-python

A docker image that includes:

- python3.6 setup
- pep8, pyflakes, pylint checkers
- unit test coverage modules
- yapf for code reformatting
- ipython for playing around with the library
- sphinx to generate API docs (has plantuml support)

## Init Python project

The recommended way is to use [cookiecutter](https://github.com/audreyr/cookiecutter) tool:

    cookiecutter gh:gurunars/python-library

## Working with the code

Requirements:

- unix*
- make
- docker 17+

Enter make help:

    cd %PROJECT%
    make help

It might take a bit of time while Docker downloads the image for the first time.
Though since Alpine linux is used as a base it should not take too long.

Afterwards use `make help` output as a guide for your project work.
