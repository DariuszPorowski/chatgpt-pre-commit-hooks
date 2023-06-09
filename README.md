# 🤖 ChatGPT / OpenAI pre-commit-hooks

[![pre-commit][pre-commit-image]][pre-commit-link]
[![PyPI - version][pypi-version-image]][pypi-version-link]
[![PyPI - python version][pypi-pyversions-image]][pypi-pyversions-link]
[![PyPI - downloads][pypi-stats-image]][pypi-stats-link]
[![GitHub - CI][github-ci-image]][github-ci-link]

Pre-commit hooks collection that utilizes ChatGPT and OpenAI platform to validate changes made to the codebase.

- [🎣 Hooks](#-hooks)
  - [`chatgpt-commit-message`](#chatgpt-commit-message)
- [📥 Prerequisites setup](#-prerequisites-setup)
  - [OpenAI Platform](#openai-platform)
  - [Azure OpenAI Service](#azure-openai-service)
  - [Setting environment variables](#setting-environment-variables)
  - [pre-commit setup](#pre-commit-setup)
- [📦 Hooks setup](#-hooks-setup)
  - [Remote repository reference (preferred)](#remote-repository-reference-preferred)
  - [Local repository reference](#local-repository-reference)
- [🛠️ Advanced configuration](#️-advanced-configuration)
  - [Extra environment variables](#extra-environment-variables)
  - [Arguments](#arguments)
  - [`--env-prefix`](#--env-prefix)
  - [Variables precedence](#variables-precedence)
- [💸 Payments](#-payments)
- [👥 Contributing](#-contributing)
- [📄 License](#-license)

## 🎣 Hooks

### `chatgpt-commit-message`

Hook that uses OpenAI's ChatGPT API to generate a summary of changes made to a codebase and use it to populate the commit message automatically.

- ⚙️ Read about hook's specific [configuration](https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/blob/main/docs/chatgpt_commit_message.md).

![chatgpt-commit-message](https://raw.githubusercontent.com/dariuszporowski/chatgpt-pre-commit-hooks/main/docs/assets/demos/chatgpt_commit_message.gif)

## 📥 Prerequisites setup

Hooks support [OpenAI Platform](https://platform.openai.com) and [Azure OpenAI Service](https://azure.microsoft.com/products/cognitive-services/openai-service).

### OpenAI Platform

OpenAI API Key is mandatory to run hooks and has to be setup via an environment variable.

1. Create your [API Key](https://platform.openai.com/account/api-keys), and get your Organization ID from [Organization settings](https://platform.openai.com/account/org-settings)

    ![OpenAI API Key](https://raw.githubusercontent.com/dariuszporowski/chatgpt-pre-commit-hooks/main/assets/images/openai-platform-api-key.png)

    ![OpenAI Organization ID](https://raw.githubusercontent.com/dariuszporowski/chatgpt-pre-commit-hooks/main/assets/images/openai-platform-org-id.png)

1. Store values as an environment variables:
    - `OPENAI_API_KEY` for API Key
    - `OPENAI_ORGANIZATION` for Organization ID

    Example:

    ```shell
    export OPENAI_API_KEY="sk-xxxxxx"
    export OPENAI_ORGANIZATION="org-xxxxxx"
    ```

> 💡 **HINT**
>
> How to setup environment variables? see: [Setting environment variables](#setting-environment-variables)

### Azure OpenAI Service

1. Go to [Azure Portal](https://portal.azure.com), and get `API Key`, `Endpoint`, `Model deployment name`, and `api-version`.

    ![Azure OpenAI API Key and Endpoint](https://raw.githubusercontent.com/dariuszporowski/chatgpt-pre-commit-hooks/main/assets/images/azure-openai-service-key-endpoint.png)

    ![Azure OpenAI Model](https://raw.githubusercontent.com/dariuszporowski/chatgpt-pre-commit-hooks/main/assets/images/azure-openai-service-models.png)

    The latest supported `api-version` you can get from [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#chat-completions)

1. Store values as an environment variables:
    - `OPENAI_API_TYPE` put `azure` to specified OpenAI provider
    - `OPENAI_API_KEY` for API Key
    - `OPENAI_API_BASE` for Endpoint
    - `OPENAI_API_VERSION` for `api-version`
    - `OPENAI_MODEL` for Model deployment name

    Example:

    ```shell
    export OPENAI_API_TYPE="azure"
    export OPENAI_API_KEY="xxxxxx"
    export OPENAI_API_BASE="https://xxxxxx.openai.azure.com/"
    export OPENAI_API_VERSION="2023-03-15-preview"
    export OPENAI_MODEL="xxxxx-gpt-35-turbo"
    ```

> 💡 **HINT**
>
> How to setup environment variables? see: [Setting environment variables](#setting-environment-variables)

### Setting environment variables

Linux/MacOS example:

```shell
export OPENAI_API_KEY="sk-xxxxxx"
```

Windows `powershell` example:

```powershell
$env:OPENAI_API_KEY="sk-xxxxxx"
```

Windows `cmd` example:

```console
set OPENAI_API_KEY=sk-xxxxxx
```

> ⚠️ **NOTE**
>
> The above example stores the environment variable temporarily for the current session. To store it permanently, please follow [Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)

### pre-commit setup

Before you start, ensure you have `pre-commit` installed in your repository. Below is just an essential quick start. Follow official pre-commit [install](https://pre-commit.com/#install) documentation for advanced scenarios.

```shell
# install using pip
pip install pre-commit

# check if working - expected print with version like `pre-commit 3.2.2`
pre-commit --version
```

Add to your `.pre-commit-config.yaml` top level `default_install_hook_types` section (for more information, follow [Confining hooks to run at certain stages](https://pre-commit.com/#confining-hooks-to-run-at-certain-stages))

```yaml
default_install_hook_types:
  - pre-commit # this is default hook type, equivalent to classic `pre-commit install` command
  - prepare-commit-msg # this type is not enabled by default, please enable it - equivalent to `pre-commit install --hook-type prepare-commit-msg` command
  - ... # rest of hook types what are you using, if any
```

next:

```shell
# setup the git repo for hooks
pre-commit install

# (optional) periodically run updates to your pre-commit config to make sure you always have the latest version of the hooks
pre-commit autoupdate
```

## 📦 Hooks setup

### Remote repository reference (preferred)

Add to your `.pre-commit-config.yaml`

```yaml
default_install_hook_types:
  - pre-commit
  - prepare-commit-msg
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: vX.Y.Z  # Use the ref you want to point at, see ⚠️ NOTE below!
    hooks:
      - id: <id1> # follow 🎣 Hooks section to see available hooks IDs
      - id: <id2> # follow 🎣 Hooks section to see available hooks IDs
      - id: ...
```

Example:

```yaml
default_install_hook_types:
  - pre-commit
  - prepare-commit-msg
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: v0.1.3
    hooks:
      - id: chatgpt-commit-message
```

> ⚠️ **NOTE**
>
> For the `rev:` always try to use the latest version. You can check the latest release under [GitHub Releases](https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/releases/latest)

### Local repository reference

1. Install or add [PyPI](https://pypi.org/project/chatgpt-pre-commit-hooks) package to your project.

   - if you are using [pip](https://pip.pypa.io):

     ```shell
     pip install --upgrade chatgpt-pre-commit-hooks
     ```

   - or include it in a `requirements.txt` file in your project:

     ```text
     chatgpt-pre-commit-hooks~=0.1.3
     ```

      and run:

     ```shell
     pip install -r requirements.txt
     ```

   - or, even better, in the `dev` section of your `pyproject.toml` file:

     ```toml
     [project.optional-dependencies]
     dev = ["chatgpt-pre-commit-hooks"]
     ```

      and run:

     ```shell
     pip install .[dev]
     ```

   - or, if you are using [poetry](https://python-poetry.org) as a package manager:

     ```shell
     poetry add chatgpt-pre-commit-hooks --group dev
     ```

1. Add to your `.pre-commit-config.yaml`

    ```yaml
    default_install_hook_types:
      - pre-commit
      - prepare-commit-msg
    repos:
      - repo: local
        hooks:
          - id: <id> # follow 🎣 Hooks section to see available hooks IDs
            name: <name> # any name you'd like to set
            entry: chatgpt-pre-commit-hooks
            args:
              - "--hook"
              - "<id>" # follow 🎣 Hooks section to see available hooks IDs
              - "..." # rest of args what you'd like to set (optional)
            language: system
    ```

    Example:

    ```yaml
    default_install_hook_types:
      - pre-commit
      - prepare-commit-msg
    repos:
    - repo: local
        hooks:
        - id: chatgpt-commit-message
          name: ChatGPT commit message
          entry: chatgpt-pre-commit-hooks
          args:
            - "--hook"
            - "chatgpt-commit-message"
            - "--description"
            - "--emoji"
          language: system
    ```

## 🛠️ Advanced configuration

### Extra environment variables

In addition to the environment variables listed in the [📥 Prerequisites setup](#-prerequisites-setup) section, you can set several configurations using extra environment variables.

| Name                |  Type  |     Default     | Description                                                                                                                                  |
|:--------------------|:------:|:---------------:|:---------------------------------------------------------------------------------------------------------------------------------------------|
| `OPENAI_MAX_TOKENS` |  int   |      1024       | [What are tokens and how to count them?](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)                  |
| `OPENAI_MODEL`      | string | `gpt-3.5-turbo` | [Model endpoint compatibility](https://platform.openai.com/docs/models/model-endpoint-compatibility) - check `/v1/chat/completions` endpoint |
| `OPENAI_PROXY`      | string |    _not set_    | http/https client proxy                                                                                                                      |

### Arguments

Any environment variable can be overridden by hard-coded arguments in `pre-commit-config.yaml`, except `OPENAI_API_KEY`, `OPENAI_ORGANIZATION`.

| Name                  |  Type  |  Default  | Description                                                                                                       |
|:----------------------|:------:|:---------:|:------------------------------------------------------------------------------------------------------------------|
| `--env-prefix`        | string | _not set_ | Set prefix for environment variables allowing multiple configurations. Read more: [`--env-prefix`](#--env-prefix) |
| `--openai-max-tokens` |  int   | _not set_ | Overrides `OPENAI_MAX_TOKENS`                                                                                     |
| `--openai-proxy`      | string | _not set_ | Overrides `OPENAI_PROXY`                                                                                          |
| `--openai-model`      | string | _not set_ | Overrides `OPENAI_MODEL`                                                                                          |
| `--openai-api-base`   | string | _not set_ | Overrides `OPENAI_API_BASE`                                                                                       |
| `--openai-api-type`   | string | _not set_ | Overrides `OPENAI_API_TYPE`                                                                                       |

Example:

```yaml
default_install_hook_types:
  - pre-commit
  - prepare-commit-msg
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: vX.Y.Z
    hooks:
      - id: ... # follow 🎣 Hooks section to see available hooks IDs
        args:
          - "--env-prefix"
          - "personal"
          - "--openai-max-tokens"
          - "512"
          - ...
```

### `--env-prefix`

It's a special argument where you can mark prefixes for your environment variables. This allows you to set many configurations depending on the project, account, profile, etc., for example, `personal`, `work`. Fallback is a global environment variable if prefixed isn't found.

For instance, if your prefix is `personal`, then the environment variable must be set `PERSONAL__OPENAI_MAX_TOKENS`, meaning the structure is `<prefix>__<base_env_name>` - two underscores `__` between `prefix` and `base_env_name`.

Example:

```shell
export PERSONAL__OPENAI_API_KEY="sk-xxxxxx"
export WORK__OPENAI_API_KEY="sk-xxxxxx"
```

### Variables precedence

1. hard-coded arguments, for example `--openai-max-tokens`
1. prefixed environment variable, for example `PERSONAL__OPENAI_MAX_TOKENS`
1. global environment variable, for example `OPENAI_MAX_TOKENS`

## 💸 Payments

Project by default uses `gpt-3.5-turbo` model because of [its lower cost](https://openai.com/pricing). You have to pay for your own OpenAI API requests.

## 👥 Contributing

Contributions to the project are welcome! Please follow [Contributing Guide](https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/blob/main/CONTRIBUTING.md).

## 📄 License

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
