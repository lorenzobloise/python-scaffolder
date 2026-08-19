from pathlib import Path

def test_directories_creates_directories(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["docs/", "tests"]}
    Directories().run(tmp_path, config)

    docs_dir: Path = tmp_path / "docs/"
    tests_dir: Path = tmp_path / "tests"

    assert docs_dir.exists()
    assert docs_dir.is_dir()
    assert tests_dir.exists()
    assert tests_dir.is_dir()

def test_directories_creates_empty_directories(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["docs/"]}
    Directories().run(tmp_path, config)

    created_dir: Path = tmp_path / "docs/"

    assert len(list(created_dir.iterdir())) == 0

def test_directories_creates_nested_directories(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["src/mypackage/utils"]}
    Directories().run(tmp_path, config)

    nested_dir = tmp_path / "src/mypackage/utils"
    assert nested_dir.exists()
    assert nested_dir.is_dir()

def test_directories_is_idempotent(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["docs"]}
    Directories().run(tmp_path, config)
    Directories().run(tmp_path, config)  # second time: should not raise any exception

    assert (tmp_path / "docs").is_dir()


# --- _build_dir_path ---

def test_build_dir_path_returns_directory_as_path_for_plain_name(tmp_path):
    from python_scaffolder.steps.directories import Directories

    result = Directories()._build_dir_path(tmp_path, "docs")

    assert result == Path("docs")


def test_build_dir_path_returns_project_dir_name_for_project_dir_token(tmp_path):
    from python_scaffolder.steps.directories import Directories

    result = Directories()._build_dir_path(tmp_path, "<project_dir>")

    assert result == Path(tmp_path.name)


# --- run with <project_dir> ---

def test_directories_creates_project_dir(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["<project_dir>"]}
    Directories().run(tmp_path, config)

    project_dir: Path = tmp_path / tmp_path.name
    assert project_dir.exists()
    assert project_dir.is_dir()


def test_directories_creates_project_dir_alongside_plain_directories(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["<project_dir>", "docs"]}
    Directories().run(tmp_path, config)

    assert (tmp_path / tmp_path.name).is_dir()
    assert (tmp_path / "docs").is_dir()


def test_build_dir_path_replaces_project_dir_token_preserving_suffix(tmp_path):
    from python_scaffolder.steps.directories import Directories

    result = Directories()._build_dir_path(tmp_path, "<project_dir>/src")

    assert result == Path(tmp_path.name) / "src"


def test_directories_creates_project_dir_with_suffix(tmp_path):
    from python_scaffolder.steps.directories import Directories

    config = {"directories": ["<project_dir>/src"]}
    Directories().run(tmp_path, config)

    project_dir: Path = tmp_path / tmp_path.name / "src"
    assert project_dir.exists()
    assert project_dir.is_dir()
