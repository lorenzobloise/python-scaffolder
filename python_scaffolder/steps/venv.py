import subprocess
import sys
from pathlib import Path

from python_scaffolder.utils import _get_python_version, _get_python_interpreter
from python_scaffolder.steps.step import Step

def _pip_path(project_path: Path) -> Path:
    """Return the path to pip inside the .venv, cross-platform."""
    if sys.platform == "win32":
        return project_path / ".venv" / "Scripts" / "pip"
    return project_path / ".venv" / "bin" / "pip"

class Venv(Step):

    @property
    def name(self) -> str:
        return "venv"

    def _find_python_interpreter(self, path: Path) -> str:
        python_version: str | None = _get_python_version(path)
        if not python_version:
            return sys.executable
        python_interpreter: str | None = _get_python_interpreter(python_version)
        if not python_interpreter:
            self.error(f"Python interpreter not found for version {python_version}")
            return
        return python_interpreter

    def run(self, path: Path, config: dict) -> None:
        """
        Create a .venv inside path using the Python version set in the .python-version file,
        or the current Python interpreter if the file does not exist.
        If config['packages'] is non-empty, install them via the venv's pip
        """
        venv_path: Path = path / ".venv"
        python_interpreter: str = self._find_python_interpreter(path)
        subprocess.run(
            [python_interpreter, "-m", "venv", str(venv_path)],
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
            self.success(f"Created .venv, installed: {', '.join(packages)}")
        else:
            self.success("Created .venv")
