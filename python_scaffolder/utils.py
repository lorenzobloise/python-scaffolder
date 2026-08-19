import json
from pathlib import Path
from tqdm import tqdm

PYTHON_SCAFFOLDER_PATH: Path = Path.home() / ".python-scaffolder"
PYTHON_INTERPRETERS_INFO_PATH: Path = PYTHON_SCAFFOLDER_PATH / ".cache/python_interpreters"

_CARRIAGE_RETURN_SEQUENCE: str = "\r"
_HIDE_CURSOR: str = "\033[?25l"
_SHOW_CURSOR: str = "\033[?25h"

def _log(msg: str, file=None, start: str="", end: str="\n"):
    tqdm.write(s=f"{start}{msg}", file=file, end=end)

class BusinessException(Exception):
    pass

def _get_python_version(path: Path) -> str | None:
    python_version_file: Path = path / ".python-version"
    if not python_version_file.exists():
        return None
    return python_version_file.read_text()

def _get_python_interpreter(python_version: str, cache_path: Path=PYTHON_INTERPRETERS_INFO_PATH) -> str | None:
    if not cache_path.exists():
        return None
    with open(cache_path, 'r', encoding='utf-8') as f:
        python_interpreters_info: list[dict[str, str]] = json.load(f)
    for info in python_interpreters_info:
        if info["version"] == python_version:
            return info["path"]
    return None
