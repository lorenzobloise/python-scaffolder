import subprocess
import sys
from pathlib import Path

from python_scaffolder.steps.step import Step, LogLabel

def _pip_path(project_path: Path) -> Path:
    """Return the path to pip inside the .venv, cross-platform."""
    if sys.platform == "win32":
        return project_path / ".venv" / "Scripts" / "pip"
    return project_path / ".venv" / "bin" / "pip"

class Venv(Step):

    @property
    def name(self) -> str:
        return "venv"

    def run(self, path: Path, config: dict) -> None:
        """
        Create a .venv inside path using the current Python interpreter.
        If config['packages'] is non-empty, install them via the venv's pip
        """
        venv_path: Path = path / ".venv"
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        packages: list[str] = config.get("packages", [])
        if packages:
            pip: Path = _pip_path(path)
            subprocess.run(
                [str(pip), "install"] + packages,
                check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )
            self.log(f"Created .venv, installed: {', '.join(packages)}", log_label=LogLabel.SUCCESS)
        else:
            self.log("Created .venv", log_label=LogLabel.SUCCESS)
