import subprocess
from pathlib import Path

from python_scaffolder.steps.step import Step

class Git(Step):

    @property
    def name(self) -> str:
        return "git"

    def _git_init(self, path: Path):
        subprocess.run(
            ["git", "init", str(path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def _git_set_user(self, path: Path, config: dict):
        result = subprocess.run(
            ["git", "config", "get", "user.name"],
            capture_output=True,
            text=True,
            check=True
        )
        default_user_name: str = result.stdout.strip() or result.stderr.strip()
        user_name: str = config.get("user.name", default_user_name) or default_user_name
        subprocess.run(
            ["git", "-C", str(path), "config", "set", "user.name", user_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        result = subprocess.run(
            ["git", "config", "get", "user.email"],
            capture_output=True,
            text=True,
            check=True
        )
        default_user_email: str = result.stdout.strip() or result.stderr.strip()
        user_email: str = config.get("user.email", default_user_email) or default_user_email
        subprocess.run(
            ["git", "-C", str(path), "config", "set", "user.email", user_email],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def _git_create_branches(self, path: Path, config: dict):
        default_branch: str = config.get("default_branch", "main")
        subprocess.run(
            ["git", "-C", str(path), "checkout", "-b", default_branch],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        branches: list[str] = config.get("branches", []) or []
        for branch in branches:
            if branch == default_branch:
                continue # Already created
            subprocess.run(
                ["git", "-C", str(path), "checkout", "-b", branch],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    def run(self, path: Path, config: dict) -> None:
        """
        Initialize a git repository at path,
        configures username and email and check out the configured default branch.
        Then creates other specified branchs.
        config['default_branch'] defaults to 'main' if absent.
        """
        self._git_init(path)
        self._git_set_user(path, config)
        self._git_create_branches(path, config)
        self.success("Initialized repository")
