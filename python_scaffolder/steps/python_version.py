import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from python_scaffolder.steps.step import Step

class PythonVersion(Step):

    @property
    def name(self) -> str:
        return "python-version"

    def __get_python_info(self, executable: str) -> dict[str, str] | None:
        """Returns the information of the Python interpreter."""
        try:
            result = subprocess.run(
                [executable, "-c",
                 "import sys; "
                 "print(sys.executable); "
                 "print(sys.version_info.major); "
                 "print(sys.version_info.minor); "
                 "print(sys.version_info.micro)"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode != 0:
                return None
            lines = result.stdout.strip().splitlines()
            if len(lines) != 4:
                return None
            info: dict[str, str] = {
                "path": lines[0],
                "version": f"{lines[1]}.{lines[2]}.{lines[3]}"
            }
            return info
        except (OSError, subprocess.SubprocessError) as e:
            print(f"\n{str(e)}\n")
            return None

    def __find_python_executables(self) -> set[str]:
        """Finds possible Python interpreters on the local machine"""
        candidates: set[str] = set()
        # Python running this program
        candidates.add(sys.executable)
        # Interpreters present in PATH
        names: set[str] = {"python", "python3"}
        # Add also the names 'python3.x' present in PATH
        # without knowing beforehand which versions are installed
        path_dirs: list[str] = os.environ.get("PATH", "").split(os.pathsep)
        for directory in path_dirs:
            if not directory:
                continue
            try:
                for entry in Path(directory).iterdir():
                    name: str = entry.name.lower()
                    if platform.system() == "Windows":
                        # On Windows only consider .exe files
                        if entry.suffix.lower() != ".exe":
                            continue
                    if (
                        name == "python"
                        or name == "python3"
                        or name.startswith("python3.")
                    ):
                        candidates.add(str(entry))
            except (OSError, PermissionError):
                pass
        # Add python/python3 using shutil.which
        for name in names:
            path: str | None = shutil.which(name)
            if path:
                candidates.add(path)
        # Windows Python Launcher
        if platform.system() == "Windows":
            py_launcher: str | None = shutil.which("py")
            if py_launcher:
                try:
                    result = subprocess.run(
                        [py_launcher, "-0p"],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if result.returncode == 0:
                        for line in result.stdout.splitlines():
                            line = line.strip()
                            if not line.startswith("-"):
                                continue
                            parts = line.split()
                            if len(parts) < 2:
                                continue
                            path = parts[-1]
                            if os.path.isfile(path):
                                candidates.add(path)
                except (OSError, subprocess.SubprocessError) as e:
                    print(f"py error: {e}")
                    pass
        return candidates

    def _find_all_python_versions(self) -> list[str]:
        """Returns all detected Python installations."""
        results: list[str] = []
        seen: set[str] = set()
        for executable in self.__find_python_executables():
            info: dict[str, str] | None = self.__get_python_info(executable)
            if not info:
                continue
            # Normalize the path to avoid duplicates
            try:
                normalized_path: str = os.path.normcase(
                    os.path.realpath(info["path"])
                )
            except OSError:
                normalized_path: str = os.path.normcase(info["path"])
            if normalized_path in seen:
                continue
            seen.add(normalized_path)
            if not len(info["version"].split(".")) == 3:
                continue # Badly formatted version
            results.append(info["version"])
        # Sort by version (latest first)
        results.sort(
            key=lambda x: tuple(map(int, x.split("."))),
            reverse=True
        )
        return results

    def _map_specific_python_interpreter(self, python_version: str, python_interpreters: list[str]) -> str | None:
        """
        Given a python version (es. '3.13') and a list of interpreters (es. ['3.14.3', '3.13.7', '3.11.9'])
        returns the corresponding interpreter for the given version (i.e. '3.13.7') or None if
        there isn't any match
        """
        formatted_python_interpreters: dict[str, str] = {".".join(interpreter.split(".")[:-1]): interpreter for interpreter in python_interpreters}
        return formatted_python_interpreters.get(python_version)

    def run(self, path: Path, config: dict) -> None:
        """
        Checks whether the python version specified in config is present on the local machine.
        If not, raises an exception.
        Then create a .python-version file useful in other steps.
        """
        python_version: str | None = config.get("version", None)
        if not python_version:
            self.error("Python version not configured.")
            return
        python_interpreters: list[str] = self._find_all_python_versions()
        python_interpreter: str | None = self._map_specific_python_interpreter(python_version, python_interpreters)
        if not python_interpreter:
            self.error(f"Python version {python_version} not installed on local machine.")
            return
        python_version_file: Path = path / ".python-version"
        python_version_file.write_text(python_interpreter)
        self.success(f"Python version set to {python_interpreter}")
