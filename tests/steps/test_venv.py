import sys
from unittest.mock import patch, MagicMock

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


# --- _find_python_interpreter ---

def test_find_python_interpreter_returns_sys_executable_when_no_version_file(tmp_path):
    """_find_python_interpreter() falls back to sys.executable when .python-version is absent."""
    from python_scaffolder.steps.venv import Venv

    result = Venv()._find_python_interpreter(tmp_path)

    assert result == sys.executable


def test_find_python_interpreter_returns_interpreter_from_version_file(tmp_path):
    """_find_python_interpreter() returns the interpreter resolved from .python-version."""
    from python_scaffolder.steps.venv import Venv

    (tmp_path / ".python-version").write_text("3.13.7")

    with patch("python_scaffolder.steps.venv._get_python_interpreter", return_value="/usr/bin/python3.13") as mock_get:
        result = Venv()._find_python_interpreter(tmp_path)

    mock_get.assert_called_once_with("3.13.7")
    assert result == "/usr/bin/python3.13"


def test_find_python_interpreter_calls_error_when_interpreter_not_found(tmp_path):
    """_find_python_interpreter() calls self.error() when _get_python_interpreter returns None."""
    from python_scaffolder.steps.venv import Venv

    (tmp_path / ".python-version").write_text("3.13.7")

    step = Venv()
    step.error = MagicMock()

    with patch("python_scaffolder.steps.venv._get_python_interpreter", return_value=None):
        step._find_python_interpreter(tmp_path)

    step.error.assert_called_once()


def test_run_uses_interpreter_from_version_file(tmp_path):
    """run() passes the interpreter from .python-version to the venv creation command."""
    from python_scaffolder.steps.venv import Venv

    (tmp_path / ".python-version").write_text("3.13.7")

    with patch("python_scaffolder.steps.venv._get_python_interpreter", return_value="/usr/bin/python3.13"):
        with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
            mock_run.return_value = None
            Venv().run(tmp_path, {"packages": []})

    venv_call = mock_run.call_args_list[0]
    assert venv_call.args[0][0] == "/usr/bin/python3.13"
