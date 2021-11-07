import argparse
from logging import getLogger
from pathlib import Path

import sagemaker
from sagemaker.estimator import Estimator

from metamaker.aws import get_session
from metamaker.commands.sagemaker.sagemaker import SageMakerCommand
from metamaker.config import Config

logger = getLogger(__name__)


@SageMakerCommand.register("deploy")
class DeployWithSagemakerCommand(SageMakerCommand):
    """deploy model with sagemaker"""

    def setup(self) -> None:
        self.parser.add_argument("-j", "--training-job", type=str, required=True)
        self.parser.add_argument("--config", type=Path, default=Path("metamaker.yaml"))

    def run(self, args: argparse.Namespace) -> None:
        config = Config.load_yaml(args.config)

        boto_session = get_session()
        sagemaker_session = sagemaker.Session(boto_session=boto_session)

        estimator = Estimator.attach(args.training_job, sagemaker_session=sagemaker_session)

        estimator.deploy(
            endpoint_name=config.inference.endpoint_name,
            instance_type=config.inference.instance.type,
            initial_instance_count=config.inference.instance.count,
        )
