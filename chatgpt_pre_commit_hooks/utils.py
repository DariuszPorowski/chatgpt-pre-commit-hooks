"""``utils``.

A module containing utility functions.
"""

import subprocess


class Utils:
    """Utils."""

    def cmd_output(self, commands: list[str]) -> str:
        """Run cmd command.

        Args:
        commands: list of commands.

        Returns:
        Get `str` output.
        """
        try:
            result = self.__cmd_output(commands)
        except subprocess.CalledProcessError:
            result = ""

        return result

    def __cmd_output(self, commands: list[str]) -> str:
        """Run cmd command.

        Args:
        commands: list of commands.

        Returns:
        Get `str` output.
        """
        output = subprocess.run(commands, capture_output=True, encoding="utf-8", check=True)  # noqa: S603
        result = ""
        if output.returncode == 0 and output.stdout is not None:
            result = output.stdout
        elif output.stderr:
            result = output.stderr

        return result.strip()
