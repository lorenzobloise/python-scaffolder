from pathlib import Path

from python_scaffolder.steps.step import Step

class Directories(Step):

    @property
    def name(self) -> str:
        return "directories"

    def run(self, path: Path, config: dict) -> None:
        """
        Create an empty directory from the directory list in config.
        """
        directories: list[str] = config.get("directories", [])
        for d in directories:
            dir_path: Path = path / Path(d)
            dir_path.mkdir(parents=True, exist_ok=True)
        self.success(f"Created directories: {', '.join(directories)}")
