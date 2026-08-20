"""Tests for python_scaffolder.steps.dependencies"""

import sys
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_instance():
    from python_scaffolder.steps.dependencies import Dependencies

    instance = Dependencies()
    instance.success = MagicMock()
    instance.error = MagicMock()
    return instance


# ---------------------------------------------------------------------------
# _pip_path
# ---------------------------------------------------------------------------

def test_pip_path_unix(tmp_path):
    from python_scaffolder.steps.dependencies import _pip_path

    with patch("python_scaffolder.steps.dependencies.sys.platform", "linux"):
        result = _pip_path(tmp_path)

    assert result == tmp_path / ".venv" / "bin" / "pip"


def test_pip_path_windows(tmp_path):
    from python_scaffolder.steps.dependencies import _pip_path

    with patch("python_scaffolder.steps.dependencies.sys.platform", "win32"):
        result = _pip_path(tmp_path)

    assert result == tmp_path / ".venv" / "Scripts" / "pip"


# ---------------------------------------------------------------------------
# _find_python_interpreter
# ---------------------------------------------------------------------------

def test_find_python_interpreter_returns_sys_executable_when_no_version_file(tmp_path):
    instance = _make_instance()

    with (
        patch("python_scaffolder.steps.dependencies._get_python_version", return_value=None),
        patch("python_scaffolder.steps.dependencies._get_python_interpreter") as mock_interp,
    ):
        result = instance._find_python_interpreter(tmp_path)

    assert result == sys.executable
    mock_interp.assert_not_called()


def test_find_python_interpreter_returns_interpreter_for_detected_version(tmp_path):
    instance = _make_instance()

    with (
        patch("python_scaffolder.steps.dependencies._get_python_version", return_value="3.12.1"),
        patch("python_scaffolder.steps.dependencies._get_python_interpreter", return_value="/usr/bin/python3.12"),
    ):
        result = instance._find_python_interpreter(tmp_path)

    assert result == "/usr/bin/python3.12"


def test_find_python_interpreter_calls_error_when_interpreter_not_found(tmp_path):
    instance = _make_instance()

    with (
        patch("python_scaffolder.steps.dependencies._get_python_version", return_value="3.12.1"),
        patch("python_scaffolder.steps.dependencies._get_python_interpreter", return_value=None),
    ):
        instance._find_python_interpreter(tmp_path)

    instance.error.assert_called_once()
    assert "3.12.1" in instance.error.call_args.args[0]


def test_find_python_interpreter_returns_none_when_interpreter_not_found(tmp_path):
    instance = _make_instance()

    with (
        patch("python_scaffolder.steps.dependencies._get_python_version", return_value="3.12.1"),
        patch("python_scaffolder.steps.dependencies._get_python_interpreter", return_value=None),
    ):
        result = instance._find_python_interpreter(tmp_path)

    assert result is None


# ---------------------------------------------------------------------------
# _create_venv
# ---------------------------------------------------------------------------

def test_create_venv_runs_venv_module(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_find_python_interpreter", return_value="/usr/bin/python3.12"),
        patch("python_scaffolder.steps.dependencies.subprocess.run") as mock_run,
    ):
        instance._create_venv(tmp_path)

    mock_run.assert_called_once()
    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "/usr/bin/python3.12"
    assert "-m" in cmd
    assert "venv" in cmd


def test_create_venv_targets_dot_venv_directory(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_find_python_interpreter", return_value="/usr/bin/python3.12"),
        patch("python_scaffolder.steps.dependencies.subprocess.run") as mock_run,
    ):
        instance._create_venv(tmp_path)

    cmd = mock_run.call_args.args[0]
    assert str(tmp_path / ".venv") in cmd


def test_create_venv_calls_success(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_find_python_interpreter", return_value="/usr/bin/python3.12"),
        patch("python_scaffolder.steps.dependencies.subprocess.run"),
    ):
        instance._create_venv(tmp_path)

    instance.success.assert_called_once()


# ---------------------------------------------------------------------------
# _create_requirements_file
# ---------------------------------------------------------------------------

def test_create_requirements_file_creates_file(tmp_path):
    instance = _make_instance()
    instance._create_requirements_file(tmp_path, ["requests", "flask"])

    assert (tmp_path / "requirements.txt").exists()


def test_create_requirements_file_writes_packages(tmp_path):
    instance = _make_instance()
    instance._create_requirements_file(tmp_path, ["requests", "flask"])

    content = (tmp_path / "requirements.txt").read_text()
    assert "requests" in content
    assert "flask" in content


def test_create_requirements_file_sorts_packages_alphabetically(tmp_path):
    instance = _make_instance()
    instance._create_requirements_file(tmp_path, ["zlib", "aiohttp", "requests"])

    lines = (tmp_path / "requirements.txt").read_text().splitlines()
    assert lines == sorted(lines)


def test_create_requirements_file_one_package_per_line(tmp_path):
    instance = _make_instance()
    packages = ["requests", "flask", "click"]
    instance._create_requirements_file(tmp_path, packages)

    lines = (tmp_path / "requirements.txt").read_text().splitlines()
    assert len(lines) == len(packages)


def test_create_requirements_file_empty_packages(tmp_path):
    instance = _make_instance()
    instance._create_requirements_file(tmp_path, [])

    content = (tmp_path / "requirements.txt").read_text()
    assert content == ""


def test_create_requirements_file_calls_success(tmp_path):
    instance = _make_instance()
    instance._create_requirements_file(tmp_path, ["requests"])

    instance.success.assert_called_once()


# ---------------------------------------------------------------------------
# _install_packages
# ---------------------------------------------------------------------------

def test_install_packages_invokes_pip(tmp_path):
    instance = _make_instance()

    with patch("python_scaffolder.steps.dependencies.subprocess.run") as mock_run:
        instance._install_packages(tmp_path, ["requests", "flask"])

    cmd = mock_run.call_args.args[0]
    assert "install" in cmd


def test_install_packages_uses_venv_pip(tmp_path):
    instance = _make_instance()
    expected_pip = str(tmp_path / ".venv" / "bin" / "pip")

    with (
        patch("python_scaffolder.steps.dependencies.sys.platform", "linux"),
        patch("python_scaffolder.steps.dependencies.subprocess.run") as mock_run,
    ):
        instance._install_packages(tmp_path, ["requests"])

    cmd = mock_run.call_args.args[0]
    assert cmd[0] == expected_pip


def test_install_packages_passes_all_packages(tmp_path):
    instance = _make_instance()
    packages = ["requests", "flask", "click"]

    with patch("python_scaffolder.steps.dependencies.subprocess.run") as mock_run:
        instance._install_packages(tmp_path, packages)

    cmd = mock_run.call_args.args[0]
    for pkg in packages:
        assert pkg in cmd


def test_install_packages_calls_success(tmp_path):
    instance = _make_instance()

    with patch("python_scaffolder.steps.dependencies.subprocess.run"):
        instance._install_packages(tmp_path, ["requests"])

    instance.success.assert_called_once()


# ---------------------------------------------------------------------------
# run — orchestration
# ---------------------------------------------------------------------------


def test_run_does_not_create_venv_by_default(tmp_path):
    instance = _make_instance()

    with patch.object(instance, "_create_venv") as mock_venv:
        instance.run(tmp_path, {})

    mock_venv.assert_not_called()


def test_run_creates_venv_when_create_venv_is_true(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_create_venv") as mock_venv,
        patch.object(instance, "_create_requirements_file"),
        patch.object(instance, "_install_packages"),
    ):
        instance.run(tmp_path, {"create_venv": True})

    mock_venv.assert_called_once_with(tmp_path)


def test_run_installs_packages_when_create_venv_and_packages_present(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_create_venv"),
        patch.object(instance, "_create_requirements_file"),
        patch.object(instance, "_install_packages") as mock_install,
    ):
        instance.run(tmp_path, {"create_venv": True, "packages": ["requests"]})

    mock_install.assert_called_once_with(tmp_path, ["requests"])


def test_run_does_not_install_packages_without_create_venv(tmp_path):
    """Packages are listed in requirements.txt but NOT installed if create_venv is False."""
    instance = _make_instance()

    with (
        patch.object(instance, "_create_requirements_file"),
        patch.object(instance, "_install_packages") as mock_install,
    ):
        instance.run(tmp_path, {"packages": ["requests"]})

    mock_install.assert_not_called()


def test_run_does_not_install_when_packages_empty_and_create_venv_true(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_create_venv"),
        patch.object(instance, "_create_requirements_file"),
        patch.object(instance, "_install_packages") as mock_install,
    ):
        instance.run(tmp_path, {"create_venv": True, "packages": []})

    mock_install.assert_not_called()


def test_run_passes_packages_to_requirements_file(tmp_path):
    instance = _make_instance()
    packages = ["requests", "flask"]

    with patch.object(instance, "_create_requirements_file") as mock_req:
        instance.run(tmp_path, {"packages": packages})

    mock_req.assert_called_once_with(tmp_path, packages)


def test_run_treats_false_create_venv_as_disabled(tmp_path):
    instance = _make_instance()

    with (
        patch.object(instance, "_create_venv") as mock_venv,
        patch.object(instance, "_create_requirements_file"),
    ):
        instance.run(tmp_path, {"create_venv": False})

    mock_venv.assert_not_called()
