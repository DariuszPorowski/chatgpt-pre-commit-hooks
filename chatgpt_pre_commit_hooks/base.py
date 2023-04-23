"""Base module."""

import argparse
import logging
import os
import sys

import openai
import tiktoken

from chatgpt_pre_commit_hooks.logger import Logger
from chatgpt_pre_commit_hooks.utils import Utils

PASS = 0
FAIL = 1


class ChatGptPreCommitHooks:
    """TODO."""

    def __init__(self) -> None:
        """TODO."""
        self.args_global, unparsed, self.args_parser = self.__get_args_global()

        self.logger = Logger(__name__, level=self.args_global.log_level.upper())
        self.log = self.logger.logger
        self.log.debug(f"SYS_ARGV: {sys.argv}")
        self.log.debug(f"ARGS_GLOBAL: {self.args_global}")
        self.log.debug(f"ARGS_GLOBAL_UNPARSED: {unparsed}")
        self.__check_openai_api_key()
        self.utils = Utils()
        self.git_repo_path = "."

    def __get_args_global(self) -> tuple[argparse.Namespace, list[str], argparse.ArgumentParser]:
        """Get input arguments."""
        parser = argparse.ArgumentParser(prog="chatgpt-pre-commit-hooks")
        parser.add_argument("--log-level", choices=[key.lower() for key in logging._nameToLevel], default="error", required=False)  # args.log_level  # noqa: SLF001
        parser.add_argument("--hook", type=str.lower, default=None, required=False)  # args.env_prefix
        parser.add_argument("--env-prefix", type=str, default=None, required=False)  # args.env_prefix

        temp_args, unparsed = parser.parse_known_args()
        temp_env_prefix = temp_args.env_prefix
        env_prefix = ""
        if temp_env_prefix is not None and temp_env_prefix:
            env_prefix = f"{temp_env_prefix.upper()}__"

        parser.add_argument("--openai-model", type=str, default=os.environ.get(f"{env_prefix}OPENAI_MODEL", "gpt-3.5-turbo"))  # args.openai_model
        parser.add_argument("--openai-max-tokens", type=int, default=os.environ.get(f"{env_prefix}OPENAI_MAX_TOKENS", "1024"))  # args.openai_max_tokens
        parser.add_argument("--openai-api-base", type=str, default=os.environ.get(f"{env_prefix}OPENAI_API_BASE", openai.api_base))  # args.openai_api_base
        parser.add_argument("--openai-api-type", type=str.lower, default=os.environ.get(f"{env_prefix}OPENAI_API_TYPE", openai.api_type))  # args.openai_api_type
        parser.add_argument("--openai-proxy", type=str, default=os.environ.get(f"{env_prefix}OPENAI_PROXY", None), required=False)  # args.openai_proxy
        parser.add_argument(
            "--openai-api-key",
            type=str,
            default=os.environ.get(f"{env_prefix}OPENAI_API_KEY", openai.api_key),
            help=argparse.SUPPRESS,
        )  # args.openai_api_key

        temp_args, unparsed = parser.parse_known_args()
        temp_openai_api_type = temp_args.openai_api_type
        if temp_openai_api_type == "azure":
            parser.add_argument(
                "--openai-api-version",
                type=str,
                default=os.environ.get(f"{env_prefix}OPENAI_API_VERSION", "2023-03-15-preview"),
                help=argparse.SUPPRESS,
            )  # args.openai_api_version
        else:
            parser.add_argument(
                "--openai-organization",
                type=str,
                default=os.environ.get(f"{env_prefix}OPENAI_ORGANIZATION", openai.organization),
                help=argparse.SUPPRESS,
            )  # args.openai_organization
        args, unparsed = parser.parse_known_args()
        return args, unparsed, parser

    def __check_openai_api_key(self) -> None:
        """Check API Key."""
        if self.args_global.openai_api_key is None:
            self.log.error("OPENAI_API_KEY is not set")
            sys.exit(FAIL)

    def get_openai_chat_response(self, messages: list[dict[str, str]]) -> str:
        """Get OpenAI Chat Response."""
        if self.log.isEnabledFor(logging.DEBUG):
            openai.debug = True

        openai.api_key = self.args_global.openai_api_key
        openai.api_base = self.args_global.openai_api_base
        openai.api_type = self.args_global.openai_api_type
        openai.proxy = self.args_global.openai_proxy

        # ref: https://platform.openai.com/docs/api-reference/chat-completions/create
        # ref: https://platform.openai.com/docs/guides/chat
        if self.args_global.openai_api_type == "azure":
            model = None
            engine = self.args_global.openai_model
            api_version = self.args_global.openai_api_version
        else:
            openai.organization = self.args_global.openai_organization
            model = self.args_global.openai_model
            engine = None
            api_version = None

        response = openai.ChatCompletion.create(
            model=model,
            engine=engine,
            api_version=api_version,
            messages=messages,
            max_tokens=int(self.args_global.openai_max_tokens),
            temperature=0,
            top_p=0.1,
        )
        self.log.debug(f"OPENAI_CHAT_RESPONSE: {response}")

        return response["choices"][0]["message"]["content"]  # type: ignore  # noqa: PGH003

    def num_tokens_from_messages(self, messages: list[dict[str, str]], model: str) -> int:
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":
            # Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
        if model == "gpt-4":
            # Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.
            return self.num_tokens_from_messages(messages, model="gpt-4-0314")
        if model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            error_msg = f"""num_tokens_from_messages() is not implemented for model {model}.
                See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            self.log.error(error_msg)
            self.self_exit(FAIL)
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        self.log.debug(f"NUM_TOKENS: {num_tokens}")
        return num_tokens

    def self_exit(self, exit_code: int) -> None:
        """TODO."""
        raise SystemExit(exit_code)
