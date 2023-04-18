#!/usr/bin/env python3
"""chatgpt-commit-message pre-commit-hook.

A pre-commit hook that utilizes ChatGPT to summarize changes made to the codebase on the 'git commit' event.
The commit message is then used to populate the commit message automatically.
"""

import logging
import os
import sys
from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from pathlib import Path
from typing import Dict, List, Optional

import openai
import tiktoken
from git.repo import Repo

logging.basicConfig(level=logging.NOTSET)
# logging.basicConfig(level=logging.DEBUG, filename="debug.log", filemode="w")  # noqa: ERA001


def get_args() -> Namespace:
    """Get input arguments."""
    logging.debug(f"SYS_ARGV: {sys.argv}")
    parser = ArgumentParser()
    parser.add_argument("commit_msg_filename", nargs="?", default=None)  # args.commit_msg_filename
    parser.add_argument("prepare_commit_message_source", nargs="?", default=None)  # args.prepare_commit_message_source
    parser.add_argument("commit_object_name", nargs="?", default=None)  # args.commit_object_name
    parser.add_argument("--max-char-count", type=int, default=10000)  # args.max_char_count
    parser.add_argument("--emoji", action=BooleanOptionalAction, default=False)  # args.emoji
    parser.add_argument("--description", action=BooleanOptionalAction, default=False)  # args.description
    parser.add_argument("--env-prefix", type=str, default=None, required=False)  # args.env_prefix
    parser.add_argument("--openai-model", type=str, default=None, required=False)  # args.openai_model
    parser.add_argument("--openai-max-tokens", type=int, default=None, required=False)  # args.openai_max_tokens
    parser.add_argument("--openai-api-base", type=str, default=None, required=False)  # args.openai_api_base
    parser.add_argument("--openai-api-type", type=str, default=None, required=False)  # args.openai_api_type
    parser.add_argument("--openai-proxy", type=str, default=None, required=False)  # args.openai_proxy
    args = parser.parse_args()
    logging.debug(f"ARGS: {args}")
    return args


def get_git_diff(max_char_count: int, git_repo_path: str) -> str:
    """Get git diff of staged changes - full or stat only.

    - full - if length of diff is less than max_char_count
    - stat - if length of diff is more than max_char_count
    """
    repo = Repo(git_repo_path)
    diff = repo.git.diff(staged=True)
    if len(diff) > max_char_count:
        diff = repo.git.diff(staged=True, stat=True)
    logging.debug(f"GIT_DIFF: {diff}")
    return diff


def get_user_commit_message(commit_msg_file_path: str, prepare_commit_message_source: Optional[str]) -> Optional[str]:
    """Get user commit message (if specified)."""
    logging.debug(f"PREPARE_COMMIT_MESSAGE_SOURCE: {prepare_commit_message_source}")
    user_commit_message = None
    if prepare_commit_message_source == "message" or prepare_commit_message_source is None:
        commit_msg_file = Path(commit_msg_file_path)
        commit_msg_file_wrapper = commit_msg_file.open(encoding="utf-8")
        lines = [line for line in commit_msg_file_wrapper.readlines() if not line.startswith("#") and line.strip()]
        commit_msg_file_wrapper.close()
        logging.debug(f"USER_COMMIT_MESSAGE_LINES: {lines}")
        if lines != []:
            user_commit_message = "".join(lines).strip()

    logging.debug(f"USER_COMMIT_MESSAGE: {user_commit_message}")

    if user_commit_message is not None:
        skip_keywords = ["#no-ai", "#no-openai", "#no-chatgpt", "#no-gpt", "#skip-ai", "#skip-openai", "#skip-chatgpt", "#skip-gpt"]
        if any(skip_keyword.casefold() in user_commit_message.casefold() for skip_keyword in skip_keywords):
            logging.debug(f"USER_COMMIT_MESSAGE: {user_commit_message} - SKIPPED")
            sys.exit(0)

    return user_commit_message


def _get_openai_config(args: Namespace) -> Dict[str, Optional[str]]:
    """Get OpenAI API Key from environment variable."""
    env_prefix = ""
    if args.env_prefix is not None:
        env_prefix = f"{args.env_prefix.upper()}__"

    # https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
    openai_api_key = os.environ.get(f"{env_prefix}OPENAI_API_KEY", openai.api_key)  # $env:OPENAI_API_KEY
    if openai_api_key is None or not openai_api_key:
        raise ValueError(f"`{env_prefix}OPENAI_API_KEY` environment variable is not set.")

    openai_model = os.environ.get(f"{env_prefix}OPENAI_MODEL", "gpt-3.5-turbo")  # $env:OPENAI_MODEL
    if args.openai_model is not None:
        openai_model = args.openai_model

    openai_max_tokens = os.environ.get(f"{env_prefix}OPENAI_MAX_TOKENS", "1024")  # $env:OPENAI_MAX_TOKENS
    if args.openai_max_tokens is not None:
        openai_max_tokens = str(args.openai_max_tokens)

    openai_api_type = os.environ.get(f"{env_prefix}OPENAI_API_TYPE", openai.api_type)  # $env:OPENAI_API_TYPE
    if args.openai_api_type is not None:
        openai_api_type = args.openai_api_type

    openai_organization = None
    if openai_api_type is not None and openai_api_type == openai.api_type:
        openai_organization = os.environ.get(f"{env_prefix}OPENAI_ORGANIZATION", openai.organization)  # $env:OPENAI_ORGANIZATION

    openai_api_base = os.environ.get(f"{env_prefix}OPENAI_API_BASE", openai.api_base)  # $env:OPENAI_API_BASE
    if args.openai_api_base is not None:
        openai_api_base = args.openai_api_base

    openai_proxy = os.environ.get(f"{env_prefix}OPENAI_PROXY", None)  # $env:OPENAI_PROXY
    if args.openai_proxy is not None:
        openai_proxy = args.openai_proxy

    return {
        "openai_api_key": openai_api_key,
        "openai_organization": openai_organization,
        "openai_api_base": openai_api_base,
        "openai_api_type": openai_api_type,
        "openai_proxy": openai_proxy,
        "openai_model": openai_model,
        "openai_max_tokens": openai_max_tokens,
    }


def get_openai_chat_prompt_messages(user_commit_message: Optional[str], git_diff: str, args: Namespace) -> List[Dict[str, str]]:
    """Get prompt messages."""
    role_system = [
        "You are a software engineer assistant to write a 'Commit message with scope'.",
        "You aim to suggest a clean commit message in the 'Conventional Commits' convention.",
        "You will get an output from the 'git diff --staged' or 'git diff --staged --stat' command, and you will suggest a commit message.",
    ]
    role_user = [git_diff]

    # GitMoji
    if args.emoji is True:
        role_system.append("Use the 'GitMoji convention' to preface the commit with the UNICODE characters format.")
        role_system.append("Do not use shortcode representation.")
    else:
        role_system.append("Do not preface the commit message with anything.")

    # description
    if args.description is True:
        role_system.append("Add a short description to the commit message in the body section of why these changes were made.")
        role_system.append('Omit "This commit" at the beginning - briefly describe changes.')
        role_system.append("Each sentence of the description should be in new line.")
    else:
        role_system.append("Do not describe changes; just simply output without any explanation - the final commit message MUST have only one line!")

    # User message
    if user_commit_message is not None:
        role_system.append("The user has already specified the commit message; please consider it as a suggestion if applicable.")
        role_system.append("The user's message starts after the 'USER-MESSAGE:' marker.")
        role_system.append("Therefore, do not include the user message in the commit message.")
        role_user.append(f"\n\nUSER-MESSAGE: {user_commit_message}")

    role_system.append("Use the present tense.")
    role_system.append("Lines must be at most 72 characters.")

    role_system_prompt = " ".join(role_system)
    role_user_prompt = " ".join(role_user)

    logging.debug(f"ROLE_SYSTEM_PROMPT: {role_system_prompt}")
    logging.debug(f"ROLE_USER_PROMPT: {role_user_prompt}")

    return [
        {"role": "system", "content": role_system_prompt},
        {"role": "user", "content": role_user_prompt},
    ]


def get_openai_chat_response(messages: List[Dict[str, str]], args: Namespace) -> str:
    """Get OpenAI Chat Response."""
    config = _get_openai_config(args)
    logging.debug(f"CONFIG: {config}")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        _num_tokens_from_messages(messages, str(config["openai_model"]))
        openai.debug = True

    openai.api_key = config["openai_api_key"]
    openai.organization = config["openai_organization"]
    openai.api_base = config["openai_api_base"]
    openai.api_type = config["openai_api_type"]
    openai.proxy = config["openai_proxy"]

    # ref: https://platform.openai.com/docs/api-reference/chat-completions/create
    # ref: https://platform.openai.com/docs/guides/chat
    response = openai.ChatCompletion.create(
        model=config["openai_model"],
        messages=messages,
        max_tokens=int(config["openai_max_tokens"]),
        temperature=0,
        top_p=0.1,
    )
    logging.debug(f"OPENAI_CHAT_RESPONSE: {response}")

    return response["choices"][0]["message"]["content"]


def _num_tokens_from_messages(messages: List[Dict[str, str]], model: str) -> int:
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        # Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.
        return _num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    if model == "gpt-4":
        # Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.
        return _num_tokens_from_messages(messages, model="gpt-4-0314")
    if model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}.
            See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""",
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    logging.debug(f"NUM_TOKENS: {num_tokens}")
    return num_tokens


def set_commit_message(commit_msg_file_path: str, commit_msg: str) -> None:
    """Set the suggested commit message."""
    commit_msg_file = Path(commit_msg_file_path)
    commit_msg_file_wrapper = commit_msg_file.open("r+", encoding="utf-8")
    current_content = commit_msg_file_wrapper.read().strip()
    commit_msg_file_wrapper.seek(0, 0)
    commit_msg_file_wrapper.write(f"{commit_msg}\n\n{current_content}")
    commit_msg_file_wrapper.close()


def main() -> int:
    """Main function of module."""
    try:
        args = get_args()
        user_commit_message = get_user_commit_message(args.commit_msg_filename, args.prepare_commit_message_source)
        git_diff = get_git_diff(args.max_char_count, ".")
        openai_chat_prompt_messages = get_openai_chat_prompt_messages(user_commit_message, git_diff, args)
        openai_chat_response = get_openai_chat_response(openai_chat_prompt_messages, args)
        set_commit_message(args.commit_msg_filename, openai_chat_response)
    except Exception as error:
        raise Exception(f"Sorry, something went wrong: {error}") from error  # noqa: TRY002
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
