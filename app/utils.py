import os
from pathlib import Path
import sys
from loguru import logger


def setup_logger():
    log_directory = Path(__file__).parent.parent / "logs"
    log_directory.mkdir(exist_ok=True)

    if True:
        logger.add(
            sink=log_directory / "ai_bot.log",
            level="DEBUG",
            rotation="20 MB",
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

    if False:
        logger.add(
            sink=stdout,
            level="DEBUG",
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
