from pathlib import Path
from tqdm import tqdm

from python_scaffolder.config import get_step_config
from python_scaffolder.steps import dotenv, git, gitignore, precommit, venv
from python_scaffolder.steps.step import Step
from python_scaffolder.utils import _log

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
    _log(Step._format_msg(msg=f"\nCreating project at {path}...\n"))
    path.mkdir(parents=True, exist_ok=False)

    for step_name, StepModule in tqdm(_STEPS, total=len(_STEPS), mininterval=0.0, leave=False):
        _log(Step._format_msg(msg="Loading...", step_name=step_name))
        step_config: dict | None = get_step_config(config, step_name)
        if not step_config:
            _log(Step._format_msg(msg="Skipping: not configured", step_name=step_name))
            continue
        StepModule().run(path, step_config)

    _log(Step._format_msg(msg=f"\nDone. Project ready at {path}\n"))
