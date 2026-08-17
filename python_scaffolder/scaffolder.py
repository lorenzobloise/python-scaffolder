from pathlib import Path

from python_scaffolder.config import get_step_config
from python_scaffolder.steps import dotenv, git, gitignore, precommit, venv

_STEPS = [
    ("git", git.Git),
    ("gitignore", gitignore.Gitignore),
    ("precommit", precommit.Precommit),
    ("venv", venv.Venv),
    ("dotenv", dotenv.Dotenv)
]

def run(path: Path, config: dict) -> None:
    """
    Create the project directory and run each configured step in order.
    Steps whose section is absent from config are skipped.
    If a step raises, execution halts immediately (no cleanup)
    """
    print(f"Creating project at {path}...\n")
    path.mkdir(parents=True, exist_ok=False)

    for step_name, StepModule in _STEPS:
        step_config: dict | None = get_step_config(config, step_name)
        if not step_config:
            print(f"Skipping {step_name}: not configured")
            continue
        StepModule().run(path, step_config)

    print(f"\nDone. Project ready at {path}")
