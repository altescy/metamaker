from metamaker.commands.subcommand import Subcommand


@Subcommand.register("run")
class RunCommand(Subcommand):
    """execute metamaker"""

    def setup(self) -> None:
        self.parser.add_argument("handler", type=str)
