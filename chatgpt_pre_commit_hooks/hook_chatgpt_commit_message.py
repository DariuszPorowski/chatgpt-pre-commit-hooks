#!/usr/bin/env python3

"""chatgpt-commit-message pre-commit-hook module.

A pre-commit hook that utilizes ChatGPT to summarize changes made to the codebase on the 'git commit' event.
The commit message is then used to populate the commit message automatically.
"""


import argparse
from pathlib import Path
from typing import Optional

from chatgpt_pre_commit_hooks.base import FAIL, PASS, ChatGptPreCommitHooks


class ChatGptCommitMessage(ChatGptPreCommitHooks):
    """TODO."""

    def __init__(self) -> None:
        """TODO."""
        super().__init__()
        self.args = self.__get_args_hook()

    def __call__(self) -> int:
        """TODO."""
        return self.__main()

    def __get_args_hook(self) -> argparse.Namespace:
        """Get input arguments."""
        self.args_parser.add_argument("--max-char-count", type=int, default=10000)  # args.max_char_count
        self.args_parser.add_argument("--emoji", action=argparse.BooleanOptionalAction, default=False)  # args.emoji
        self.args_parser.add_argument("--description", action=argparse.BooleanOptionalAction, default=False)  # args.description
        self.args_parser.add_argument("commit_msg_filename", nargs="?", type=Path, default=Path(".git", "COMMIT_EDITMSG"))  # args.commit_msg_filename
        self.args_parser.add_argument("prepare_commit_message_source", nargs="?", default=None)  # args.prepare_commit_message_source
        self.args_parser.add_argument("commit_object_name", nargs="?", default=None)  # args.commit_object_name
        self.args_parser.add_argument(dest="rest", nargs=argparse.REMAINDER)
        args, unparsed = self.args_parser.parse_known_args()
        self.log.debug(f"ARGS_HOOK: {args}")
        self.log.debug(f"ARGS_HOOK_UNPARSED: {unparsed}")
        return args

    def __get_git_diff(self) -> str:
        """Get git diff of staged changes - full or stat only.

        - full - if length of diff is less than max_char_count
        - stat - if length of diff is more than max_char_count
        """
        commands = ["git", "diff", "--staged", "--cached"]
        diff = self.utils.cmd_output(commands)
        if len(diff) > self.args.max_char_count:
            commands = ["git", "diff", "--staged", "--cached", "--stat"]
            diff = self.utils.cmd_output(commands)
        self.log.debug(f"GIT_DIFF: {diff}")
        return diff

    def __get_user_commit_message(self) -> Optional[str]:
        """Get user commit message (if specified)."""
        self.log.debug(f"PREPARE_COMMIT_MESSAGE_SOURCE: {self.args.prepare_commit_message_source}")
        user_commit_message = None
        if self.args.prepare_commit_message_source == "message" or self.args.prepare_commit_message_source is None:
            commit_msg_file_wrapper = self.args.commit_msg_filename.open("rt", encoding="utf-8")
            lines = [line for line in commit_msg_file_wrapper.readlines() if not line.startswith("#") and line.strip()]
            commit_msg_file_wrapper.close()
            self.log.debug(f"USER_COMMIT_MESSAGE_LINES: {lines}")
            if lines != []:
                user_commit_message = "".join(lines).strip()

        self.log.debug(f"USER_COMMIT_MESSAGE: {user_commit_message}")

        if user_commit_message is not None:
            skip_keywords = ["#no-ai", "#no-openai", "#no-chatgpt", "#no-gpt", "#skip-ai", "#skip-openai", "#skip-chatgpt", "#skip-gpt"]
            if any(skip_keyword.casefold() in user_commit_message.casefold() for skip_keyword in skip_keywords):
                self.log.debug(f"USER_COMMIT_MESSAGE: {user_commit_message} - SKIPPED")
                self.self_exit(PASS)

        return user_commit_message

    def __get_openai_chat_prompt_messages(self) -> list[dict[str, str]]:
        """Get prompt messages."""
        role_system = [
            "You are a software engineer assistant to write a 'Commit message with scope'.",
            "You aim to suggest a clean commit message in the 'Conventional Commits' convention.",
            "You will get an output from the 'git diff --staged' or 'git diff --staged --stat' command, and you will suggest a commit message.",
        ]
        role_user = [self.__get_git_diff()]

        # GitMoji
        if self.args.emoji is True:
            role_system.append("Use the 'GitMoji convention' to preface the commit with the UNICODE characters format.")
            role_system.append("Do not use shortcode representation.")
        else:
            role_system.append("Do not preface the commit message with anything.")

        # description
        if self.args.description is True:
            role_system.append("Add a short description to the commit message in the body section of why these changes were made.")
            role_system.append('Omit "This commit" at the beginning - briefly describe changes.')
            role_system.append("Each sentence of the description should be in new line.")
        else:
            role_system.append("Do not describe changes; just simply output without any explanation - the final commit message MUST have only one line!")

        user_commit_message = self.__get_user_commit_message()
        # User message
        if user_commit_message is not None:
            role_system.append("The user has already specified the commit message; please consider it as a suggestion if applicable.")
            role_system.append("Do not include user message itself in the final commit message and do not put any note why.")
            role_system.append("The user's message starts after the 'USER-MESSAGE:'.")
            role_user.append(f"\n\nUSER-MESSAGE: {user_commit_message}")

        role_system.append("Use the present tense.")
        role_system.append("Lines must be at most 72 characters.")

        role_system_prompt = " ".join(role_system)
        role_user_prompt = " ".join(role_user)

        self.log.debug(f"ROLE_SYSTEM_PROMPT: {role_system_prompt}")
        self.log.debug(f"ROLE_USER_PROMPT: {role_user_prompt}")

        return [
            {"role": "system", "content": role_system_prompt},
            {"role": "user", "content": role_user_prompt},
        ]

    def __set_commit_message(self) -> None:
        """Set the suggested commit message."""
        messages = self.__get_openai_chat_prompt_messages()
        commit_msg = self.get_openai_chat_response(messages)
        commit_msg_file_wrapper = self.args.commit_msg_filename.open("wt", encoding="utf-8")
        commit_msg_file_wrapper.write(commit_msg)
        commit_msg_file_wrapper.close()

    def __main(self) -> int:
        """Main function of module."""
        try:
            self.__set_commit_message()
        except (ValueError, TypeError) as err:
            self.log.exception(err.with_traceback(err.__traceback__))
            return FAIL
        else:
            return PASS


def main() -> int:
    """Hook entry point."""
    chatgpt_commit_message = ChatGptCommitMessage()
    return int(chatgpt_commit_message())


if __name__ == "__main__":
    raise SystemExit(main())
