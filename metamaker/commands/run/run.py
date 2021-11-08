import sys

from metamaker.commands.subcommand import Subcommand


@Subcommand.register("run")
class RunCommand(Subcommand):
    """execute metamaker"""

    def setup(self) -> None:
        sys.path.append(".")
        self.parser.add_argument("handler", type=str)
