from pathlib import Path
import pytest
from unittest.mock import patch

def test_scaffolder_creates_project_directory(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {} # no steps configured

    run(project_path, config)

    assert project_path.exists()
    assert project_path.is_dir()

def test_scaffolder_runs_step_when_section_present(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {"git": {"default_branch": "main"}}

    with patch("python_scaffolder.scaffolder.git.run") as mock_git:
        run(project_path, config)

    mock_git.assert_called_once_with(project_path, {"default_branch": "main"})

def test_scaffolder_skips_step_when_section_absent(tmp_path, capsys):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {} # no git section

    with patch("python_scaffolder.scaffolder.git.run") as mock_git:
        run(project_path, config)

    mock_git.assert_not_called()
    captured = capsys.readouterr()
    assert "Skipping git" in captured.out

def test_scaffolder_runs_all_steps_when_all_configured(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {
        "git": {"default_branch": "main"},
        "gitignore": {"sections": [{"python": ["*__pycache__/"]}]},
        "precommit": {"repos": []},
        "venv": {"packages": []},
        "dotenv": {"variables": []}
    }

    with (
        patch("python_scaffolder.scaffolder.git.run") as mock_git,
        patch("python_scaffolder.scaffolder.gitignore.run") as mock_gitignore,
        patch("python_scaffolder.scaffolder.precommit.run") as mock_precommit,
        patch("python_scaffolder.scaffolder.venv.run") as mock_venv,
        patch("python_scaffolder.scaffolder.dotenv.run") as mock_dotenv,
    ):
        run(project_path, config)

    mock_git.assert_called_once()
    mock_gitignore.assert_called_once()
    mock_precommit.assert_called_once()
    mock_venv.assert_called_once()
    mock_dotenv.assert_called_once()

def test_scaffolder_halts_on_step_exception(tmp_path, capsys):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {
        "git": {"default_branch": "main"},
        "gitignore": {"sections": [{"python": ["*__pycache__/"]}]}
    }

    with (
        patch("python_scaffolder.scaffolder.git.run", side_effect=RuntimeError("git not found")),
        patch("python_scaffolder.scaffolder.gitignore.run") as mock_gitignore,
    ):
        with pytest.raises(RuntimeError, match="git not found"):
            run(project_path, config)
    mock_gitignore.assert_not_called()
