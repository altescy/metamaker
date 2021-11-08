import argparse
from pathlib import Path
from typing import Any, Dict

import yaml

from metamaker import hyperparameter
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
        self.parser.add_argument(
            "--hyperparameter-path",
            type=Path,
            default=Path("/opt/ml/input/config/hyperparameters.json"),
        )

    def run(self, args: argparse.Namespace) -> None:
        handler = MetaMaker.from_path(args.handler)
        hyperparameters = self._load_hyperparameters(args.hyperparameter_path)
        handler.train(args.dataset_path, args.artifact_path, hyperparameters)

    @staticmethod
    def _load_hyperparameters(path: Path) -> Dict[str, Any]:
        with path.open() as fp:
            hyperparameters = yaml.safe_load(fp)
            assert isinstance(hyperparameters, dict)
            return hyperparameter.deserialize(hyperparameters)
