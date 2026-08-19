from pathlib import Path

from python_scaffolder.steps.step import Step

class Directories(Step):

    @property
    def name(self) -> str:
        return "directories"

    def _build_dir_path(self, path: Path, directory: str) -> Path:
        if directory.startswith("<project_dir>"):
            return Path(directory.replace("<project_dir>", path.name))
        return Path(directory)

    def run(self, path: Path, config: dict) -> None:
        """
        Create an empty directory from the directory list in config.
        """
        directories: list[str] = config.get("directories", [])
        for d in directories:
            new_dir: Path = self._build_dir_path(path, d)
            dir_path: Path = path / new_dir
            dir_path.mkdir(parents=True, exist_ok=True)
        self.success(f"Created directories: {', '.join(directories)}")
