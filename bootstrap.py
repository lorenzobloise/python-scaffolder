from importlib.resources import files
from pathlib import Path

APP_DIR = Path.home() / ".python-scaffolder"
CONFIG_PATH = APP_DIR / "config.yaml"


def bootstrap() -> bool:
    """
    Initialize python-scaffolder user configuration.

    Returns:
        True if the default config was created.
        False if the config already existed.
    """
    if CONFIG_PATH.exists():
        print(f"[python-scaffolder] Config already exists at {CONFIG_PATH}")
        return False

    APP_DIR.mkdir(parents=True, exist_ok=True)

    default_config = files("python_scaffolder").joinpath("default_config.yaml")
    CONFIG_PATH.write_text(
        default_config.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    print(f"[python-scaffolder] Created default config, edit to customize your scaffolding: {CONFIG_PATH}")
    return True


def main() -> None:
    bootstrap()


if __name__ == "__main__":
    main()
