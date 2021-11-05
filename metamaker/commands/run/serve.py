import argparse
from pathlib import Path

import uvicorn

from metamaker import api
from metamaker.commands.run.run import RunCommand
from metamaker.config import Config
from metamaker.handler import Handler


@RunCommand.register("serve")
class ServeCommand(RunCommand):
    """serve endpoint api"""

    def setup(self) -> None:
        self.parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
        )
        self.parser.add_argument(
            "--port",
            type=int,
            default=8080,
        )
        self.parser.add_argument(
            "--artifact-path",
            type=Path,
            default=Path("/opt/ml/model/"),
        )
        self.parser.add_argument(
            "--config",
            type=Path,
            default=Path("./metamaker.yaml"),
        )

    def run(self, args: argparse.Namespace) -> None:
        config = Config.load_yaml(args.config)
        handler = Handler.from_path(config.metamaker.handler)

        app = api.create(handler=handler, artifact_path=args.artifact_path)

        uvicorn.run(app, host=args.host, port=args.port)
