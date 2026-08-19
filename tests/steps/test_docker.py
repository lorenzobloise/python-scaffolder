from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from python_scaffolder.steps.docker import Docker

@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    return tmp_path

@pytest.fixture
def step() -> Docker:
    return Docker()

# Cleanest approach: mock the template directly

def test_creates_dockerfile_at_correct_path(step: Docker, tmp_project: Path) -> None:
    template_content = "FROM python:{python_version}{digest}-slim\nCMD [\"{entry_point}\"]"
    mock_template = MagicMock(spec=Path)
    mock_template.read_text.return_value = template_content

    with patch.object(type(step), "_dockerfile_template_path", new_callable=lambda: property(
        lambda self: mock_template
    )):
        with patch("python_scaffolder.utils._get_python_version", return_value="3.11"):
            step.run(path=tmp_project, config={})

    assert (tmp_project / "Dockerfile").exists()


def test_dockerfile_uses_python_version_from_file(step: Docker, tmp_project: Path) -> None:
    mock_template = MagicMock(spec=Path)
    mock_template.read_text.return_value = "FROM python:{python_version}{digest}-slim\nCMD [\"{entry_point}\"]"

    with patch.object(type(step), "_dockerfile_template_path", new_callable=lambda: property(
        lambda self: mock_template
    )):
        with patch("python_scaffolder.steps.docker._get_python_version", return_value="3.11"):
            with patch("python_scaffolder.steps.docker._get_python_version_from_executable", return_value="3.12"):
                step.run(path=tmp_project, config={})

    content = (tmp_project / "Dockerfile").read_text()
    assert "3.11" in content
    assert "3.12" not in content


def test_dockerfile_falls_back_to_executable_version(step: Docker, tmp_project: Path) -> None:
    mock_template = MagicMock(spec=Path)
    mock_template.read_text.return_value = "FROM python:{python_version}{digest}-slim\nCMD [\"{entry_point}\"]"

    with patch.object(type(step), "_dockerfile_template_path", new_callable=lambda: property(
        lambda self: mock_template
    )):
        with patch("python_scaffolder.steps.docker._get_python_version", return_value=None):
            with patch("python_scaffolder.steps.docker._get_python_version_from_executable", return_value="3.12"):
                step.run(path=tmp_project, config={})

    content = (tmp_project / "Dockerfile").read_text()
    assert "3.12" in content


def test_dockerfile_uses_digest_from_config(step: Docker, tmp_project: Path) -> None:
    mock_template = MagicMock(spec=Path)
    mock_template.read_text.return_value = "FROM python:{python_version}{digest}-slim\nCMD [\"{entry_point}\"]"

    with patch.object(type(step), "_dockerfile_template_path", new_callable=lambda: property(
        lambda self: mock_template
    )):
        with patch("python_scaffolder.steps.docker._get_python_version", return_value="3.11"):
            step.run(path=tmp_project, config={"digest": "sha256:abc123"})

    content = (tmp_project / "Dockerfile").read_text()
    assert "@sha256:abc123" in content


def test_dockerfile_no_digest_when_not_in_config(step: Docker, tmp_project: Path) -> None:
    mock_template = MagicMock(spec=Path)
    mock_template.read_text.return_value = "FROM python:{python_version}{digest}-slim\nCMD [\"{entry_point}\"]"

    with patch.object(type(step), "_dockerfile_template_path", new_callable=lambda: property(
        lambda self: mock_template
    )):
        with patch("python_scaffolder.steps.docker._get_python_version", return_value="3.11"):
            step.run(path=tmp_project, config={})

    content = (tmp_project / "Dockerfile").read_text()
    assert "@" not in content


def test_dockerfile_uses_custom_entry_point(step: Docker, tmp_project: Path) -> None:
    mock_template = MagicMock(spec=Path)
    mock_template.read_text.return_value = "FROM python:{python_version}{digest}-slim\nCMD [\"{entry_point}\"]"

    with patch.object(type(step), "_dockerfile_template_path", new_callable=lambda: property(
        lambda self: mock_template
    )):
        with patch("python_scaffolder.steps.docker._get_python_version", return_value="3.11"):
            step.run(path=tmp_project, config={"entry_point": "app.py"})

    content = (tmp_project / "Dockerfile").read_text()
    assert "app.py" in content

def test_step_name_is_docker(step: Docker) -> None:
    assert step.name == "docker"
