from metamaker.commands.subcommand import Subcommand


@Subcommand.register("run")
class RunCommand(Subcommand):
    """execute metamaker"""
