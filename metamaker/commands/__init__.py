import argparse
from typing import Optional

from metamaker import __version__
from metamaker.commands import build  # noqa: F401
from metamaker.commands import run  # noqa: F401
from metamaker.commands import sagemaker  # noqa: F401
from metamaker.commands.subcommand import Subcommand


def create_command(prog: Optional[str] = None) -> Subcommand:
    parser = argparse.ArgumentParser(usage="%(prog)s", prog=prog)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    return Subcommand(parser)
