import re
import subprocess
from typing import Tuple

REGEX_VERSION = re.compile(r"Poetry version (\d+).(\d+).(\d+)")


def get_version() -> Tuple[int, int, int]:
    output = subprocess.run(["poetry", "--version"], capture_output=True)
    match = re.match(REGEX_VERSION, output.stdout.decode())
    if match is None:
        raise RuntimeError("Failed to get poetry version.")
    major, minor, micro = match.groups()
    return int(major), int(minor), int(micro)
