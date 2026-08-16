import subprocess
import sys
from pathlib import Path

def _pip_path(project_path: Path) -> Path:
    """Return the path to pip inside the .venv, cross-platform."""
    if sys.platform == "win32":
        return project_path / ".venv" / "Scripts" / "pip"
    return project_path / ".venv" / "bin" / "pip"

def run(path: Path, config: dict) -> None:
    """
    Create a .venv inside path using the current Python interpreter.
    If config['packages'] is non-empty, install them via the venv's pip
    """
    venv_path: Path = path / ".venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True
    )

    packages: list[str] = config.get("packages", [])
    if packages:
        pip: Path = _pip_path(path)
        subprocess.run(
            [str(pip), "install"] + packages,
            check=True
        )
        print(f"[venv]  Created .venv, installed: {', '.join(packages)}")
    else:
        print(f"[venv]  Created .venv")