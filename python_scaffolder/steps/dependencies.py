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

class Dependencies(Step):

    @property
    def name(self) -> str:
        return "dependencies"

    def _find_python_interpreter(self, path: Path) -> str:
        python_version: str | None = _get_python_version(path)
        if not python_version:
            return sys.executable
        python_interpreter: str | None = _get_python_interpreter(python_version)
        if not python_interpreter:
            self.error(f"Python interpreter not found for version {python_version}")
            return
        return python_interpreter

    def _create_venv(self, path: Path):
        venv_path: Path = path / ".venv"
        python_interpreter: str = self._find_python_interpreter(path)
        subprocess.run(
            [python_interpreter, "-m", "venv", str(venv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.success(f"Created virtual environment at {str(venv_path)}")

    def _create_requirements_file(self, path: Path, packages: list[str]):
        requirements_file: Path = path / "requirements.txt"
        lines: list[str] = []
        for package in packages:
            lines.append(package)
        requirements_file.write_text("\n".join(sorted(lines)))
        self.success(f"Created requirements file at {str(requirements_file)}")

    def _install_packages(self, path: Path, packages: list[str]):
        pip: Path = _pip_path(path)
        subprocess.run(
            [str(pip), "install"] + packages,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.success(f"Installed dependencies: {', '.join(packages)}")

    def run(self, path: Path, config: dict) -> None:
        """
        Create a .venv inside path using the Python version set in the .python-version file,
        or the current Python interpreter if the file does not exist.
        If config['packages'] is non-empty, install them via the venv's pip
        """
        create_venv: bool = config.get("create_venv", False) or False
        if create_venv:
            self._create_venv(path)
        packages: list[str] = config.get("packages", []) or []
        if packages:
            self._create_requirements_file(path, packages)
            if create_venv:
                self._install_packages(path, packages)
