import subprocess
from pathlib import Path

def run(path: Path, config: dict) -> None:
    """
    Initialize a git repository at path and check out the configured default branch.
    config['default_branch'] defaults to 'main' if absent.
    """
    branch: str = config.get("default_branch", "main")

    subprocess.run(["git", "init", str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "checkout", "-b", branch],
        check=True
    )
    print(f"[git]  Initialized repository (branch: {branch})")