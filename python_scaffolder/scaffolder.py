import itertools
from pathlib import Path
import shutil
import sys
import threading
import time
from tqdm import tqdm

from python_scaffolder.config import get_step_config
from python_scaffolder.steps import cicd, directories, docker, dotenv, git, gitignore, precommit, pyproject, python_version, venv
from python_scaffolder.steps.step import Step
from python_scaffolder.utils import _log, _CARRIAGE_RETURN_SEQUENCE, _HIDE_CURSOR, _SHOW_CURSOR, BusinessException

_STEPS = [
    ("python-version", python_version.PythonVersion),
    ("git", git.Git),
    ("gitignore", gitignore.Gitignore),
    ("precommit", precommit.Precommit),
    ("venv", venv.Venv),
    ("dotenv", dotenv.Dotenv),
    ("directories", directories.Directories),
    ("docker", docker.Docker),
    ("ci-cd", cicd.CICD),
    ("pyproject.toml", pyproject.Pyproject)
]

def _tqdm_loading(msg: str="Loading...", step_name: str="", interval: float=0.25) -> tuple:
    stop_event = threading.Event()
    spinner_bar: tqdm = tqdm(total=0, bar_format="{desc}", position=0, leave=False)

    def spinner():
        sys.stdout.write(_HIDE_CURSOR)
        sys.stdout.flush()
        time.sleep(interval)
        for symbol in itertools.cycle(["|", "/", "-", "\\"]):
            if stop_event.is_set():
                break
            line: str = Step._format_msg(msg=f"{symbol} {msg}", step_name=step_name)
            spinner_bar.set_description_str(line)
            time.sleep(interval)
        sys.stdout.write(_SHOW_CURSOR)
        sys.stdout.flush()

    thread = threading.Thread(target=spinner, daemon=True)
    thread.start()

    return stop_event, thread, spinner_bar


def run(path: Path, config: dict) -> None:
    """
    Create the project directory and run each configured step in order.
    Steps whose section is absent from config are skipped.
    If a step raises, execution halts immediately (no cleanup)
    """
    _log(Step._format_msg(msg=f"\nCreating project at {path}...\n"))
    path.mkdir(parents=True, exist_ok=False)

    progress_bar: tqdm = tqdm(_STEPS, total=len(_STEPS), position=1, mininterval=0.0, leave=False)
    try:
        for step_name, StepModule in progress_bar:
            stop_event, thread, spinner_bar = _tqdm_loading(step_name=step_name)

            try:
                step_config: dict | None = get_step_config(config, step_name)
                if not step_config:
                    _log(Step._format_msg(msg="Skipping: not configured", step_name=step_name), start=_CARRIAGE_RETURN_SEQUENCE)
                    continue
                StepModule().run(path, step_config)
            finally:
                stop_event.set()
                thread.join()
                spinner_bar.close()
    except Exception as e:
        if not isinstance(e, BusinessException):
            _log(Step._format_msg(msg=e))
        _log(Step._format_msg(msg=f"\nCleaning up {path}...\n"))
        shutil.rmtree(path)
        _log(Step._format_msg(msg="Cleaning up completed.\n"))
        sys.exit(1)
    finally:
        progress_bar.close()

    _log(Step._format_msg(msg=f"\nDone. Project ready at {path}\n"))
