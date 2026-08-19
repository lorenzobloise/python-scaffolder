from pathlib import Path
import pytest
from unittest.mock import patch

from python_scaffolder.utils import BusinessException


# --- _map_specific_python_interpreter ---

def test_map_specific_python_interpreter_returns_full_version_on_match():
    from python_scaffolder.steps.python_version import PythonVersion

    result = PythonVersion()._map_specific_python_interpreter(
        "3.13", ["3.14.3", "3.13.7", "3.11.9"]
    )

    assert result == "3.13.7"


def test_map_specific_python_interpreter_returns_none_when_version_not_present():
    from python_scaffolder.steps.python_version import PythonVersion

    result = PythonVersion()._map_specific_python_interpreter(
        "3.12", ["3.14.3", "3.13.7", "3.11.9"]
    )

    assert result is None


def test_map_specific_python_interpreter_returns_none_on_empty_list():
    from python_scaffolder.steps.python_version import PythonVersion

    result = PythonVersion()._map_specific_python_interpreter("3.13", [])

    assert result is None


def test_map_specific_python_interpreter_matches_exactly_not_by_prefix():
    from python_scaffolder.steps.python_version import PythonVersion

    # "3.1" must not match "3.13.7"
    result = PythonVersion()._map_specific_python_interpreter(
        "3.1", ["3.13.7", "3.11.9"]
    )

    assert result is None


# --- _find_all_python_versions ---

def test_find_all_python_versions_returns_sorted_descending():
    from python_scaffolder.steps.python_version import PythonVersion

    step = PythonVersion()
    versions = step._find_all_python_versions()

    assert versions == sorted(
        versions,
        key=lambda x: tuple(map(int, x.split("."))),
        reverse=True,
    )


def test_find_all_python_versions_returns_only_three_part_versions():
    from python_scaffolder.steps.python_version import PythonVersion

    versions = PythonVersion()._find_all_python_versions()

    for v in versions:
        parts = v.split(".")
        assert len(parts) == 3, f"Version '{v}' is not in major.minor.micro format"
        assert all(part.isdigit() for part in parts), f"Version '{v}' contains non-numeric parts"


def test_find_all_python_versions_includes_current_interpreter():
    import sys
    from python_scaffolder.steps.python_version import PythonVersion

    vi = sys.version_info
    current = f"{vi.major}.{vi.minor}.{vi.micro}"

    versions = PythonVersion()._find_all_python_versions()

    assert current in versions


def test_find_all_python_versions_has_no_duplicates():
    from python_scaffolder.steps.python_version import PythonVersion

    versions = PythonVersion()._find_all_python_versions()

    assert len(versions) == len(set(versions))


# --- run ---

def test_run_creates_python_version_file(tmp_path):
    import sys
    from python_scaffolder.steps.python_version import PythonVersion

    vi = sys.version_info
    minor_version = f"{vi.major}.{vi.minor}"
    full_version = f"{vi.major}.{vi.minor}.{vi.micro}"

    with patch.object(PythonVersion, "_find_all_python_versions", return_value=[full_version]):
        PythonVersion().run(tmp_path, {"version": minor_version})

    python_version_file: Path = tmp_path / ".python-version"
    assert python_version_file.exists()
    assert python_version_file.read_text() == full_version


def test_run_does_not_create_file_when_version_not_configured(tmp_path):
    from python_scaffolder.steps.python_version import PythonVersion

    with pytest.raises(BusinessException):
        PythonVersion().run(tmp_path, {})

    assert not (tmp_path / ".python-version").exists()


def test_run_does_not_create_file_when_version_not_installed(tmp_path):
    from python_scaffolder.steps.python_version import PythonVersion

    with pytest.raises(BusinessException):
        with patch.object(PythonVersion, "_find_all_python_versions", return_value=["3.11.9"]):
            PythonVersion().run(tmp_path, {"version": "3.13"})

    assert not (tmp_path / ".python-version").exists()
