import argparse
from pathlib import Path

from metamaker.commands.run.run import RunCommand
from metamaker.metamaker import MetaMaker


@RunCommand.register("train")
class TrainCommand(RunCommand):
    """train model"""

    def setup(self) -> None:
        self.parser.add_argument(
            "--dataset-path",
            type=Path,
            default=Path("/opt/ml/input/data/dataset/"),
        )
        self.parser.add_argument(
            "--artifact-path",
            type=Path,
            default=Path("/opt/ml/model/"),
        )

    def run(self, args: argparse.Namespace) -> None:
        handler = MetaMaker.from_path(args.handler)
        handler.trainer(args.dataset_path, args.artifact_path)
