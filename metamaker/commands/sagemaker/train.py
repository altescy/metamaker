import argparse
from logging import getLogger
from pathlib import Path
from typing import Dict, Optional

import sagemaker
import yaml
from sagemaker.estimator import Estimator

from metamaker import hyperparameter
from metamaker.aws import get_image_uri, get_session
from metamaker.commands.sagemaker.sagemaker import SageMakerCommand
from metamaker.config import Config

logger = getLogger(__name__)


@SageMakerCommand.register("train")
class TrainWithSagemakerCommand(SageMakerCommand):
    """train model with sagemaker"""

    def setup(self) -> None:
        self.parser.add_argument("--deploy", action="store_true")
        self.parser.add_argument("--local", action="store_true")
        self.parser.add_argument("--dataset-path", type=Path, default=Path.cwd())
        self.parser.add_argument("--artifact-path", type=Path, default=Path.cwd())
        self.parser.add_argument("--config", type=Path, default=Path("metamaker.yaml"))

    def run(self, args: argparse.Namespace) -> None:
        config = Config.load_yaml(args.config)

        boto_session = get_session()
        sagemaker_session = None if args.local else sagemaker.Session(boto_session=boto_session)

        image_uri = get_image_uri(boto_session, config.image.name)
        execution_role = "dummy/dummy" if args.local else config.training.execution_role
        instance_type = "local" if args.local else config.training.instance.type
        instance_count = 1 if args.local else config.training.instance.count
        dataset_path = f"file://{args.dataset_path.absolute()}" if args.local else config.dataset_path
        output_path = f"file://{args.artifact_path.absolute()}" if args.local else config.artifact_path
        inputs = {"dataset": dataset_path} if config.dataset_path else None

        hyperparameters: Optional[Dict[str, str]] = None
        if config.hyperparameter_path:
            with open(config.hyperparameter_path) as yamlfile:
                hyperparameters = hyperparameter.serialize(yaml.safe_load(yamlfile))

        estimator = Estimator(
            image_uri=image_uri,
            role=execution_role,
            instance_type=instance_type,
            instance_count=instance_count,
            hyperparameters=hyperparameters,
            output_path=output_path,
            sagemaker_session=sagemaker_session,
        )

        estimator.fit(inputs=inputs)

        if args.deploy:
            estimator.deploy(
                endpoint_name=config.inference.endpoint_name,
                instance_type=config.inference.instance.type,
                initial_instance_count=config.inference.instance.count,
            )
