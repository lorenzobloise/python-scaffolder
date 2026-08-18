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
