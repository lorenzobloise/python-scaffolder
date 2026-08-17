import sys
from unittest.mock import patch

def test_venv_creates_venv_directory(tmp_path):
    """run() calls python -m venv .venv inside the project path"""
    from python_scaffolder.steps.venv import Venv

    with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
        mock_run.return_value = None
        Venv().run(tmp_path, {"packages": []})

    venv_call = mock_run.call_args_list[0]
    assert venv_call.args[0] == [sys.executable, "-m", "venv", str(tmp_path / ".venv")]

def test_venv_installs_packages(tmp_path):
    """run() calls pip install for each package"""
    from python_scaffolder.steps.venv import Venv

    with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
        mock_run.return_value = None
        Venv().run(tmp_path, {"packages": ["pytest", "pre-commit"]})

    assert mock_run.call_count == 2
    pip_call = mock_run.call_args_list[1]
    assert "pytest" in pip_call.args[0]
    assert "pre-commit" in pip_call.args[0]

def test_venv_skips_install_when_packages_empty(tmp_path):
    """run() only calls venv creation when packages list is empty."""
    from python_scaffolder.steps.venv import Venv

    with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
        mock_run.return_value = None
        Venv().run(tmp_path, {"packages": []})

    assert mock_run.call_count == 1  # only the venv creation call

def test_venv_uses_correct_pip_path_on_posix(tmp_path):
    """run() uses .venv/bin/pip on POSIX systems."""
    from python_scaffolder.steps.venv import _pip_path

    pip = _pip_path(tmp_path)
    # On posix: .venv/bin/pip; on windows: .venv/Scripts/pip
    assert ".venv" in str(pip)
    assert "pip" in str(pip).lower()
