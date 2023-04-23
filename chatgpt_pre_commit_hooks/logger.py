"""Logger module."""
import logging
from pathlib import Path


class Logger:
    """Logger."""

    def __init__(self, name: str = "chatgpt_pre_commit_hooks", level: int = logging.ERROR) -> None:
        """Initialize logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        if self.logger.isEnabledFor(logging.DEBUG):
            file_handler = logging.FileHandler(filename=Path.cwd().joinpath("debug.log"), mode="w")
            self.logger.addHandler(file_handler)

    def get_level_names(self) -> list[str]:
        """Get logger level names."""
        return [key.lower() for key in logging._nameToLevel]  # noqa: SLF001
