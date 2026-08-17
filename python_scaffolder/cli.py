import sys
from pathlib import Path

from python_scaffolder import scaffolder
from python_scaffolder.config import load_config
from python_scaffolder.utils import _log

def main() -> None:
    """
    Entry point for the python-scaffolder CLI.
    Usage: python-scaffolder <path>
    """
    if len(sys.argv) != 2:
        _log("Usage: python-scaffolder <path>", file=sys.stderr)
        sys.exit(1)

    path: Path = Path(sys.argv[1]).resolve()

    if path.exists():
        _log(f"Error: directory '{path}' already exists.", file=sys.stderr)
        sys.exit(1)

    config: dict = load_config()
    scaffolder.run(path, config)
