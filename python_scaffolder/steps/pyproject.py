from importlib.resources import files
from pathlib import Path
import sys

from python_scaffolder.steps.step import Step
from python_scaffolder.utils import _get_python_version, _get_python_version_from_executable

class Pyproject(Step):

    @property
    def name(self) -> str:
        return "pyproject.toml"

    @property
    def _pyproject_templates(self) -> Path:
        return Path(
            files("python_scaffolder")
            .joinpath("assets", "pyproject")
        )

    def _format_source_dir(self, path: Path, directory: str) -> Path:
        if directory.startswith("<project_dir>"):
            return Path(directory.replace("<project_dir>", path.name))
        return Path(directory)

    def run(self, path: Path, config: dict) -> None:
        project_name: str = path.name
        python_version: str = _get_python_version(path) or _get_python_version_from_executable(sys.executable)
        dependencies: list[str] = [] # TODO
        base_template: Path = self._pyproject_templates / "template"
        file_content: str = base_template.read_text().format(
            project_name=project_name,
            python_version=f">={'.'.join(python_version.split('.')[:-1])}",
            dependencies=f"{', '.join(d for d in dependencies)}"
        )
        source_dir: str | None = config.get("source_dir") or None
        if source_dir:
            new_dir: Path = self._format_source_dir(path, source_dir)
            packages_template: Path = self._pyproject_templates / "packages"
            packages: str = packages_template.read_text().format(
                source_dir=str(new_dir)
            )
            file_content += f"\n\n{packages}"
        pyproject_toml: Path = path / "pyproject.toml"
        pyproject_toml.write_text(file_content)
        self.success("Created pyproject.toml file")
