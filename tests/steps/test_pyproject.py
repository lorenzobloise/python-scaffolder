"""Tests for python_scaffolder.steps.pyproject"""

from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_TEMPLATE = (
    "[project]\n"
    "name = {project_name}\n"
    "requires-python = >={python_version}\n"
    "dependencies = [{dependencies}]\n"
)

FAKE_PACKAGES_TEMPLATE = (
    "[tool.hatch.build.targets.wheel]\n"
    "packages = [\"{source_dir}\"]\n"
)


def _make_pyproject(python_version="3.11"):
    """Return a Pyproject instance with filesystem and version helpers mocked."""
    from python_scaffolder.steps.pyproject import Pyproject

    instance = Pyproject()

    # Mock the template directory so tests don't need real asset files
    templates_dir = MagicMock()

    def _fake_template_div(name):
        mock_file = MagicMock()
        if name == "template":
            mock_file.read_text.return_value = FAKE_TEMPLATE
        elif name == "packages":
            mock_file.read_text.return_value = FAKE_PACKAGES_TEMPLATE
        return mock_file

    templates_dir.__truediv__ = lambda self, name: _fake_template_div(name)

    instance.__class__._pyproject_templates = property(lambda self: templates_dir)

    return instance, python_version


def _run_with_version_mocks(instance, path, config, detected_version=None, executable_version="3.11.0"):
    """Call instance.run with _get_python_version helpers patched."""
    with (
        patch("python_scaffolder.steps.pyproject._get_python_version", return_value=detected_version),
        patch("python_scaffolder.steps.pyproject._get_python_version_from_executable", return_value=executable_version),
        patch.object(instance, "success"),
    ):
        instance.run(path, config)


# ---------------------------------------------------------------------------
# _format_source_dir
# ---------------------------------------------------------------------------

def test_format_source_dir_replaces_project_dir_placeholder(tmp_path):
    from python_scaffolder.steps.pyproject import Pyproject

    p = Pyproject()
    result = p._format_source_dir(tmp_path, "<project_dir>/src")
    assert result == Path(f"{tmp_path.name}/src")


def test_format_source_dir_returns_plain_path_unchanged(tmp_path):
    from python_scaffolder.steps.pyproject import Pyproject

    p = Pyproject()
    result = p._format_source_dir(tmp_path, "custom_src")
    assert result == Path("custom_src")


def test_format_source_dir_exact_placeholder_becomes_project_name(tmp_path):
    """<project_dir> alone (no suffix) should become the project directory name."""
    from python_scaffolder.steps.pyproject import Pyproject

    p = Pyproject()
    result = p._format_source_dir(tmp_path, "<project_dir>")
    assert result == Path(tmp_path.name)


# ---------------------------------------------------------------------------
# _get_dependencies
# ---------------------------------------------------------------------------

def test_get_dependencies_returns_empty_list_when_no_requirements_file(tmp_path):
    from python_scaffolder.steps.pyproject import Pyproject

    p = Pyproject()
    assert p._get_dependencies(tmp_path) == []


def test_get_dependencies_reads_packages_from_requirements_file(tmp_path):
    from python_scaffolder.steps.pyproject import Pyproject

    (tmp_path / "requirements.txt").write_text("requests\nflask")
    p = Pyproject()
    result = p._get_dependencies(tmp_path)
    assert "requests" in result
    assert "flask" in result


def test_get_dependencies_returns_one_entry_per_line(tmp_path):
    from python_scaffolder.steps.pyproject import Pyproject

    (tmp_path / "requirements.txt").write_text("requests\nflask\nclick")
    p = Pyproject()
    assert len(p._get_dependencies(tmp_path)) == 3


# ---------------------------------------------------------------------------
# run — pyproject.toml creation (no source_dir)
# ---------------------------------------------------------------------------

def test_run_creates_pyproject_toml(tmp_path):
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {})

    assert (tmp_path / "pyproject.toml").exists()


def test_run_writes_project_name(tmp_path):
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {})

    content = (tmp_path / "pyproject.toml").read_text()
    assert tmp_path.name in content


def test_run_writes_detected_python_version(tmp_path):
    """Version "3.12.1" must be truncated to ">=3.12" in the output file."""
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {}, detected_version="3.12.1")

    content = (tmp_path / "pyproject.toml").read_text()
    assert ">=3.12" in content
    assert "3.12.1" not in content  # patch segment must be stripped


def test_run_falls_back_to_executable_version_when_detection_fails(tmp_path):
    """When detection returns None, the executable version (truncated) is used."""
    instance, _ = _make_pyproject()
    _run_with_version_mocks(
        instance, tmp_path, {},
        detected_version=None,
        executable_version="3.10.4",
    )

    content = (tmp_path / "pyproject.toml").read_text()
    assert ">=3.10" in content
    assert "3.10.4" not in content  # patch segment must be stripped


def test_run_without_source_dir_does_not_include_packages_section(tmp_path):
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {})

    content = (tmp_path / "pyproject.toml").read_text()
    assert "packages" not in content


# ---------------------------------------------------------------------------
# run — source_dir handling
# ---------------------------------------------------------------------------

def test_run_with_source_dir_includes_packages_section(tmp_path):
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {"source_dir": "src"})

    content = (tmp_path / "pyproject.toml").read_text()
    assert "packages" in content


def test_run_with_plain_source_dir_writes_correct_path(tmp_path):
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {"source_dir": "my_src"})

    content = (tmp_path / "pyproject.toml").read_text()
    assert "my_src" in content


def test_run_with_project_dir_placeholder_resolves_to_project_name(tmp_path):
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {"source_dir": "<project_dir>"})

    content = (tmp_path / "pyproject.toml").read_text()
    assert tmp_path.name in content


def test_run_with_none_source_dir_does_not_include_packages_section(tmp_path):
    """An explicit None value for source_dir must behave like an absent key."""
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {"source_dir": None})

    content = (tmp_path / "pyproject.toml").read_text()
    assert "packages" not in content


def test_run_with_empty_string_source_dir_does_not_include_packages_section(tmp_path):
    """An empty string source_dir is falsy and must skip the packages section."""
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {"source_dir": ""})

    content = (tmp_path / "pyproject.toml").read_text()
    assert "packages" not in content


# ---------------------------------------------------------------------------
# run — dependencies from requirements.txt
# ---------------------------------------------------------------------------

def test_run_writes_dependencies_from_requirements_file(tmp_path):
    """Packages listed in requirements.txt must appear in pyproject.toml dependencies."""
    (tmp_path / "requirements.txt").write_text("requests\nflask")
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {})

    content = (tmp_path / "pyproject.toml").read_text()
    assert "requests" in content
    assert "flask" in content


def test_run_writes_empty_dependencies_when_no_requirements_file(tmp_path):
    """Without requirements.txt the dependencies field must be empty."""
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {})

    content = (tmp_path / "pyproject.toml").read_text()
    # The template renders: dependencies = []
    assert "dependencies = []" in content


def test_run_quotes_each_dependency(tmp_path):
    """Each dependency must be wrapped in double quotes in the output."""
    (tmp_path / "requirements.txt").write_text("requests\nflask")
    instance, _ = _make_pyproject()
    _run_with_version_mocks(instance, tmp_path, {})

    content = (tmp_path / "pyproject.toml").read_text()
    assert '"requests"' in content
    assert '"flask"' in content


# ---------------------------------------------------------------------------
# run — success notification
# ---------------------------------------------------------------------------

def test_run_calls_success(tmp_path):
    instance, _ = _make_pyproject()

    with (
        patch("python_scaffolder.steps.pyproject._get_python_version", return_value="3.11.0"),
        patch("python_scaffolder.steps.pyproject._get_python_version_from_executable", return_value="3.11.0"),
        patch.object(instance, "success") as mock_success,
    ):
        instance.run(tmp_path, {})

    mock_success.assert_called_once()
