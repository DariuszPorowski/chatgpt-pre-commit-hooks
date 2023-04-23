# Contributing Guide

I appreciate your interest in contributing to the project! This document outlines how to contribute to the project, including the contribution process, code style, and testing.

## Contribution process

To contribute, please follow these steps:

1. Fork the project name repository on GitHub.
1. Create a new branch for your feature or bug fix.
1. Setup development environment.

    ```shell
    # create virtual environment
    python3 -m venv .venv

    # activate virtual environment - see examples, based on your OS/shell

    # unix/macos with bash shell
    source .venv/bin/activate

    # unix/macos with csh shell
    source .venv/bin/activate.csh

    # unix/macos with fish shell
    source .venv/bin/activate.fish

    # windows with cmd
    .venv\Scripts\activate.bat

    # windows with powershell
    .venv\Scripts\Activate.ps1

    # install project dependencies
    pip install .[dev] .[build]

    # do test build
    python3 -m pip wheel --no-deps -w dist .
    ```

1. Make your changes and commit them with descriptive commit messages; check [Conventional Commits](https://www.conventionalcommits.org) as a suggestion.
1. Push to your forked repository.
1. Create a new pull request from your fork to this project.
1. Please ensure that your pull request includes a detailed description of your changes and that your code adheres to the code style guidelines outlined below.

## Code style

[Ruff](https://beta.ruff.rs) is used for code style checking and linting.

```shell
ruff check --fix .
```

Follow Ruff's results to style your Python code. Please ensure that your code follows these guidelines before submitting a pull request.

## Code of Conduct

All contributors are expected to adhere to the project name code of conduct. Therefore, please review it before contributing [Code of Conduct](./CODE_OF_CONDUCT.md).

## License

By contributing to this project, you agree that your contributions will be licensed under the project license.

Thank you for contributing!
