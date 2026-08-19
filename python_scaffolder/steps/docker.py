from importlib.resources import files
from pathlib import Path
import sys

from python_scaffolder.steps.step import Step
from python_scaffolder.utils import _get_python_version, _get_python_version_from_executable

class Docker(Step):

    @property
    def name(self) -> str:
        return "docker"

    @property
    def _dockerfile_template_path(self) -> Path:
        return Path(
            files("python_scaffolder")
            .joinpath("assets", "docker", "template")
        )

    def run(self, path: Path, config: dict) -> None:
        digest: str = config.get("digest", "") or ""
        if digest:
            digest = f"@{digest}"
        python_version: str = _get_python_version(path) or _get_python_version_from_executable(sys.executable)
        entry_point: str = config.get("entry_point", "main.py")
        template: Path = self._dockerfile_template_path
        file_content: str = template.read_text().format(
            version=python_version,
            digest=digest,
            entry_point=entry_point
        )
        dockerfile_path: Path = path / "Dockerfile"
        dockerfile_path.write_text(file_content)
        self.success("Created Dockerfile")
