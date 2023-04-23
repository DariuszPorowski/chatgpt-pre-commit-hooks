#!/usr/bin/env python3
"""Base entry point module."""
import argparse
import logging

from chatgpt_pre_commit_hooks.base import FAIL
from chatgpt_pre_commit_hooks.hook_chatgpt_commit_message import ChatGptCommitMessage
from chatgpt_pre_commit_hooks.logger import Logger


def get_args() -> tuple[argparse.Namespace, list[str]]:
    """Get input arguments."""
    parser = argparse.ArgumentParser(prog="chatgpt-pre-commit-hooks-wrapper")
    parser.add_argument("--hook", type=str.lower, default=None, required=False)  # args.hook
    parser.add_argument("--log-level", choices=[key.lower() for key in logging._nameToLevel], default="error", required=False)  # args.log_level  # noqa: SLF001
    args, unparsed = parser.parse_known_args()
    return args, unparsed


def set_logger(level: str) -> logging.Logger:
    """Set logger."""
    return Logger(__name__, logging.getLevelName(level.upper())).logger


def main() -> int:
    """TODO."""
    args, unparsed = get_args()
    log = set_logger(args.log_level)
    log.debug(f"ARGS_MAIN: {args}")
    log.debug(f"ARGS_MAIN_UNPARSED: {unparsed}")
    if args.hook == "chatgpt-commit-message":
        hook_return = ChatGptCommitMessage()()
    else:
        log.error(f"Unknown hook: {args.hook}")
        hook_return = FAIL

    return int(hook_return)


if __name__ == "__main__":
    raise SystemExit(main())
