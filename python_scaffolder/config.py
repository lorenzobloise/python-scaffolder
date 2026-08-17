from importlib.resources import files
from pathlib import Path
import yaml

from python_scaffolder.utils import _log

CONFIG_PATH = Path.home() / ".python-scaffolder" / "config.yaml"

def load_config() -> dict:
    """
    Load the user config from CONFIG_PATH.
    If the file does not exist, bootstrap it from the bundled default and print an informational message.
    Returns the parsed YAML as a plain dict.
    """
    if not CONFIG_PATH.exists():
        _bootstrap_config()

    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f) or {}

def _bootstrap_config() -> None:
    """Copy the bundled default_config.yaml to CONFIG_PATH."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    default = files("python_scaffolder").joinpath("default_config.yaml")
    with default.open() as src:
        CONFIG_PATH.write_text(src.read())
    _log(msg=f"Created default config at {CONFIG_PATH} - edit it to customize your scaffolding.")

def get_step_config(config: dict, step: str) -> dict | None:
    """
    Return the sub-section of config for the given step name, or None if absent.
    A step is considered disabled when its key is missing from the config.
    """
    return config.get(step)
