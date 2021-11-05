from metamaker.commands.subcommand import Subcommand


@Subcommand.register("sagemaker")
class SageMakerCommand(Subcommand):
    """execute sagemaker"""
