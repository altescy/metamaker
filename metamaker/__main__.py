import logging
import os

from metamaker.commands import create_command

if os.environ.get("METAMAKER_DEBUG"):
    LEVEL = logging.DEBUG
else:
    level_name = os.environ.get("METAMAKER_LOG_LEVEL", "INFO")
    LEVEL = logging._nameToLevel.get(level_name, logging.INFO)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=LEVEL)


def run() -> None:
    app = create_command(prog="metamaker")
    app()


if __name__ == "__main__":
    run()
