import subprocess
from pathlib import Path

from python_scaffolder.steps.step import Step, LogLabel

class Git(Step):

    @property
    def name(self) -> str:
        return "git"

    def run(self, path: Path, config: dict) -> None:
        """
        Initialize a git repository at path and check out the configured default branch.
        config['default_branch'] defaults to 'main' if absent.
        """
        branch: str = config.get("default_branch", "main")

        subprocess.run(
            ["git", "init", str(path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ["git", "-C", str(path), "checkout", "-b", branch],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.log(f"Initialized repository (branch: {branch})", log_label=LogLabel.SUCCESS)
