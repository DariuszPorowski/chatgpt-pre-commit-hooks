# chatgpt-commit-message

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Hook that uses OpenAI's ChatGPT API to generate a summary of changes made to a codebase and use it to populate the commit message automatically.

Commit message structure based on [`Commit message with scope`](https://www.conventionalcommits.org/en/v1.0.0/#commit-message-with-scope) convention from [Conventional Commits](https://www.conventionalcommits.org).

## Setup

This hook runs on the `prepare-commit-msg` stage and requires to be explicitly enabled. Unfortunately, the standard `pre-commit install` does not support the hook. To enable prepare-commit-msg support, please run the following:

```shell
pre-commit install --hook-type prepare-commit-msg
```

Add to your `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: v0.1.0 # Use the ref you want to point at, see ⚠️ NOTE below!
    hooks:
      - id: chatgpt-commit-message
```

> ⚠️ **NOTE**
>
> For the `rev:` always try to use the latest version. You can check the latest release under [GitHub Releases](https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks/releases/latest)

## Configuration

The hook can take optional arguments.

| Name               | Type | Default | Description                                                                                                                                                                                             |
|:-------------------|:----:|:-------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--max-char-count` | int  |  10000  | Send `git diff --staged --stat` results instead of the full diff of staged changes if the diff length is more than NNN characters                                                                       |
| `--emoji`          | bool |  false  | Use [GitMoji](https://gitmoji.dev) to preface commit message 💥                                                                                                                                         |
| `--description`    | bool |  false  | Add short changes summary description to the commit (see, [Commit message with description](https://www.conventionalcommits.org/en/v1.0.0/#commit-message-with-description-and-breaking-change-footer)) |

Example:

```yaml
repos:
  - repo: https://github.com/DariuszPorowski/chatgpt-pre-commit-hooks
    rev: v0.1.0 # Use the ref you want to point at, see ⚠️ NOTE below!
    hooks:
      - id: chatgpt-commit-message
        args:
          - "--max-char-count"
          - "500"
          - "--emoji"
          - "--description"
```

## Skip suggestions

If your **commit message** includes one of the keywords: `#no-ai`, `#no-openai`, `#no-chatgpt`, `#no-gpt`, `#skip-ai`, `#skip-openai`, `#skip-chatgpt`, `#skip-gpt`, then the commit suggestion will be skipped without any request to OpenAI service, and the pre-commit hook will pass.OpenAI service, and pre-commit hook will pass.

Example:

```text
Update typos in docs #no-gpt
```

## References

- [Conventional Commits](https://www.conventionalcommits.org)
- [GitMoji](https://gitmoji.dev)
- [pre-commit | prepare-commit-msg](https://pre-commit.com/index.html#prepare-commit-msg)
- [git | prepare-commit-msg](https://git-scm.com/docs/githooks#_prepare_commit_msg)
