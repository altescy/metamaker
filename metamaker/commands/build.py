import argparse
from pathlib import Path

from metamaker.commands.subcommand import Subcommand
from metamaker.config import Config
from metamaker.docker import build_image, push_image_to_ecr


@Subcommand.register("build")
class BuildCommand(Subcommand):
    """build and push docker image to ecr"""

    def setup(self) -> None:
        self.parser.add_argument("workdir", type=Path, default=Path.cwd())
        self.parser.add_argument("--push", action="store_true")
        self.parser.add_argument("--no-cache", action="store_true")
        self.parser.add_argument("--config", type=Path, default=None)

    def run(self, args: argparse.Namespace) -> None:
        config_path = args.config or args.workdir / "metamaker.yaml"

        config = Config.load_yaml(config_path)

        build_image(
            handler=config.handler,
            image_name=config.image.name,
            context_dir=args.workdir,
            includes=config.image.includes,
            excludes=config.image.excludes,
            setup=config.image.setup,
            entrypoint=config.image.entrypoint,
            no_cache=args.no_cache,
        )

        if args.push:
            push_image_to_ecr(config.image.name)
