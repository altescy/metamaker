import os
import platform
import shutil
import sys
import tempfile
from logging import getLogger
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from typing import List, Optional

from metamaker import poetry
from metamaker.aws import get_account_id, get_profile, get_session

logger = getLogger(__name__)


IMAGE_URI_TEMPLATE = "{account}.dkr.ecr.{region}.amazonaws.com/{image}:{version}"

DOCKERFILE_TEMPLATE = """
FROM python:{python_version}-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        curl \
        bzip2 \
        build-essential \
        cmake \
        git-core \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade poetry=={poetry_version}

WORKDIR /app

COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
RUN poetry install --no-dev

{dependencies}

{setup}

EXPOSE 8080
ENTRYPOINT {entrypoint}
"""


def generate_dockerfile(
    python_version: str,
    poetry_version: str,
    dependencies: List[str],
    setup: str,
    entrypoint: List[str],
) -> str:
    return DOCKERFILE_TEMPLATE.format(
        python_version=python_version,
        poetry_version=poetry_version,
        dependencies="\n".join(f"COPY {name} ./{name}" for name in dependencies),
        setup="\n".join(f"RUN {line.strip()}" for line in setup.strip().split("\n")) if setup else "",
        entrypoint="[" + ", ".join(f'"{x}"' for x in entrypoint) + "]",
    ).strip()


def build_image(
    handler: str,
    image_name: str,
    context_dir: Path,
    *,
    includes: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    setup: Optional[str] = None,
    entrypoint: Optional[List[str]] = None,
    no_cache: bool = False,
) -> None:
    includes = includes or []
    setup = setup or ""
    entrypoint = entrypoint or ["poetry", "run", "metamaker", "run", handler]

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    poetry_version = "{}.{}.{}".format(*poetry.get_version())

    dockerfile = generate_dockerfile(
        python_version=python_version,
        poetry_version=poetry_version,
        dependencies=includes,
        setup=setup,
        entrypoint=entrypoint,
    )

    logger.info("Generated dockerfile:\n%s", dockerfile)

    context_dir = context_dir.absolute()
    includes += ["pyproject.toml", "poetry.lock"]
    include_paths = [context_dir / name for name in includes]

    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = Path(tmpdir)

        for path in include_paths:
            if path.is_dir():
                shutil.copytree(path, cwd / path.name)
            else:
                shutil.copy(path, cwd / path.name)

        if (context_dir / "Dockerfile").exists():
            shutil.copy(context_dir / "Dockerfile", cwd / "Dockerfile")
        else:
            with open(cwd / "Dockerfile", "w") as fp:
                fp.write(dockerfile)

        if (context_dir / ".dockerignre").exists():
            shutil.copy(context_dir / ".dockerignore", cwd / ".dockerignore")

        if excludes:
            with open(cwd / ".dockerignore", "a") as fp:
                fp.write("\n")
                for line in excludes:
                    fp.write(line.strip() + "\n")

        commands = [
            "docker",
            "build",
            "-t",
            image_name,
            "-f",
            str(cwd / "Dockerfile"),
            ".",
        ]

        if no_cache:
            commands.append("--no-cache")

        proc = Popen(
            commands,
            cwd=context_dir,
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
        )
        proc_stdout = proc.stdout
        if proc_stdout:
            for line in iter(proc_stdout.readline, ""):
                sys.stdout.write(line)


def push_image_to_ecr(image: str) -> None:
    session = get_session()
    account = get_account_id(session)
    region = session.region_name or "ap-northeast-1"
    fullname = IMAGE_URI_TEMPLATE.format(
        account=account,
        region=region,
        image=image,
        version="latest",
    )

    logger.info("Push docker image %s to %s", image, fullname)

    ecr_client = session.client("ecr")
    try:
        ecr_client.describe_repositories(repositoryNames=[image])["repositories"]
    except ecr_client.exceptions.RepositoryNotFoundException:
        ecr_client.create_repository(repositoryName=image)
        logger.info("Created new ECR repository: %s", image)

    command_separator = ";\n"
    if platform.system() == "Windows":
        command_separator = " && "

    profile = get_profile() or ""
    docker_login_command = (
        f"aws ecr get-login-password --profile '{profile}'"
        f" | docker login --username AWS --password-stdin {account}.dkr.ecr.{region}.amazonaws.com"
    )
    docker_tag_command = f"docker tag {image} {fullname}"
    docker_push_command = f"docker push {fullname}"

    command = command_separator.join([docker_login_command, docker_tag_command, docker_push_command])

    logger.info("Executing: %s", command)
    os.system(command)
