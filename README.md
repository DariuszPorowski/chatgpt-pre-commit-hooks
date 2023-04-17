# 🤖 ChatGPT / OpenAI pre-commit-hooks

[![pre-commit][pre-commit-image]][pre-commit-link]
[![PyPI - version][pypi-version-image]][pypi-version-link]
[![PyPI - python version][pypi-pyversions-image]][pypi-pyversions-link]
[![PyPI - downloads][pypi-stats-image]][pypi-stats-link]
[![GitHub - ci][github-ci-image]][github-ci-link]

## 📥 Setup

### pre-commit setup

Before you start, ensure you have `pre-commit` installed in your repository. Below is just an essential quick start. Follow official pre-commit [install](https://pre-commit.com/#install) documentation for advanced scenarios.

```shell
# install using pip
pip install pre-commit

# check if working - expected print with version like `pre-commit 3.2.2`
pre-commit --version

# setup the git repo for hooks
pre-commit install

# periodically run updates to your pre-commit config to make sure you always have the latest version of the hooks
pre-commit autoupdate
```

### Hooks setup

#### Remote repo reference

Add to your `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: vX.Y.Z  # Use the ref you want to point at, see ⚠️ NOTE below!
    hooks:
      - id: ... # follow 🎣 Hooks section to see available hooks IDs
```

Example:

```yaml
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: v0.1.0
    hooks:
      - id: chatgpt-commit-message
```

> ⚠️ **NOTE**
>
> For the `rev:` always try to use the latest version. You can check the latest release under [GitHub Releases](https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/releases/latest)

#### Local repo reference

1. Install or add [PyPI](https://pypi.org/project/chatgpt-pre-commit-hooks) package to your project.

   - if you are using [pip](https://pip.pypa.io):

     ```shell
     pip install chatgpt-pre-commit-hooks
     ```

   - or include it in a `requirements.txt` file in your project:

     ```text
     chatgpt-pre-commit-hooks
     ```

   - or, even better, in the dev section of your `pyproject.toml` file:

     ```toml
     [project.optional-dependencies]
     dev = ["chatgpt-pre-commit-hooks"]
     ```

   - or, if you are using [poetry](https://python-poetry.org) as a package manager:

     ```shell
     poetry add chatgpt-pre-commit-hooks --group dev
     ```

2. Add to your `.pre-commit-config.yaml`

    ```yml
    repos:
      - repo: local
        hooks:
          - id: ... # follow 🎣 Hooks section to see available hooks IDs
            name: Run chatgpt-pre-commit-hooks (<name>)
            entry: chatgpt-pre-commit-hooks.<id> # follow 🎣 Hooks section to see available hooks IDs
            language: system
    ```

    Example:

    ```yml
    repos:
      - repo: local
        hooks:
          - id: chatgpt-commit-message
            name: Run chatgpt-pre-commit-hooks (chatgpt-commit-message)
            entry: chatgpt-pre-commit-hooks.chatgpt-commit-message
            language: system
    ```

### OpenAI API Key

Hooks require OpenAI access.

1. Create your [OpenAI API Key](https://platform.openai.com/account/api-keys)
1. Store API key as an environment variable (see: [Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety))

## 🎣 Hooks

### `chatgpt-commit-message`

Hook that uses OpenAI's ChatGPT API to generate a summary of changes made to a codebase and use it to populate the commit message automatically.

- Read [setup and usage](https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/blob/main/docs/chatgpt_commit_message.md) for this hook.

## License

This project is distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license.

[github-ci-image]: https://img.shields.io/github/actions/workflow/status/DariuszPorowski/chatgpt-pre-commit-hooks/workflow.ci.yml?style=flat-square&branch=main&event=push
[github-ci-link]: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/actions/workflows/workflow.ci.yml?query=branch%3Amain+event%3Apush
[pre-commit-image]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=flat-square
[pre-commit-link]: https://github.com/pre-commit/pre-commit
[pypi-version-image]: https://img.shields.io/pypi/v/chatgpt-pre-commit-hooks?style=flat-square
[pypi-version-link]: https://pypi.org/project/chatgpt-pre-commit-hooks
[pypi-pyversions-image]: https://img.shields.io/pypi/pyversions/chatgpt-pre-commit-hooks?style=flat-square
[pypi-pyversions-link]: https://pypi.org/project/chatgpt-pre-commit-hooks
[pypi-stats-image]: https://img.shields.io/pypi/dm/chatgpt-pre-commit-hooks?style=flat-square
[pypi-stats-link]: https://pypistats.org/packages/chatgpt-pre-commit-hooks
