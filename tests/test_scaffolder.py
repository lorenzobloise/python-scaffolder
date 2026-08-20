from pathlib import Path
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

    with patch("python_scaffolder.scaffolder.git.Git.run") as mock_git:
        run(project_path, config)

    mock_git.assert_called_once_with(project_path, {"default_branch": "main"})

def test_scaffolder_skips_step_when_section_absent(tmp_path, capsys):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {} # no git section

    with patch("python_scaffolder.scaffolder.git.Git.run") as mock_git:
        run(project_path, config)

    mock_git.assert_not_called()
    captured = capsys.readouterr()
    assert "Skipping" in captured.out

def test_scaffolder_runs_all_steps_when_all_configured(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path: Path = tmp_path / "my-project"
    config: dict = {
        "python-version": {"version": "3.13"},
        "git": {"default_branch": "main"},
        "gitignore": {"sections": [{"python": ["*__pycache__/"]}]},
        "precommit": {"repos": []},
        "dependencies": {"create_venv": False, "packages": []},
        "dotenv": {"variables": []},
        "directories": {"directories": []},
        "docker": {"digest": None, "entry_point": "main.py"},
        "ci-cd": {"platform": "github", "steps": []},
        "pyproject.toml": {"source_dir": "<project_dir>"}
    }

    with (
        patch("python_scaffolder.scaffolder.python_version.PythonVersion.run") as mock_python_version,
        patch("python_scaffolder.scaffolder.git.Git.run") as mock_git,
        patch("python_scaffolder.scaffolder.gitignore.Gitignore.run") as mock_gitignore,
        patch("python_scaffolder.scaffolder.precommit.Precommit.run") as mock_precommit,
        patch("python_scaffolder.scaffolder.dependencies.Dependencies.run") as mock_dependencies,
        patch("python_scaffolder.scaffolder.dotenv.Dotenv.run") as mock_dotenv,
        patch("python_scaffolder.scaffolder.directories.Directories.run") as mock_directories,
        patch("python_scaffolder.scaffolder.docker.Docker.run") as mock_docker,
        patch("python_scaffolder.scaffolder.cicd.CICD.run") as mock_cicd,
        patch("python_scaffolder.scaffolder.pyproject.Pyproject.run") as mock_pyproject
    ):
        run(project_path, config)

    mock_python_version.assert_called_once()
    mock_git.assert_called_once()
    mock_gitignore.assert_called_once()
    mock_precommit.assert_called_once()
    mock_dependencies.assert_called_once()
    mock_dotenv.assert_called_once()
    mock_directories.assert_called_once()
    mock_docker.assert_called_once()
    mock_cicd.assert_called_once()
    mock_pyproject.assert_called_once()
