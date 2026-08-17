from pathlib import Path
import pytest
from unittest.mock import patch

def test_cli_errors_when_directory_exists(tmp_path, capsys):
    from python_scaffolder.cli import main

    existing: Path = tmp_path / "existing-project"
    existing.mkdir()

    with patch("sys.argv", ["python-scaffolder", str(existing)]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0
    captured = capsys.readouterr()
    assert "already exists" in captured.out or "already exists" in captured.err

def test_cli_calls_scaffolder_with_resolved_path(tmp_path):
    from python_scaffolder.cli import main

    target: Path = tmp_path / "new-project"

    with (
        patch("sys.argv", ["python-scaffolder", str(target)]),
        patch("python_scaffolder.cli.load_config", return_value={}),
        patch("python_scaffolder.cli.scaffolder.run") as mock_run
    ):
        main()

    mock_run.assert_called_once_with(target.resolve(), {})

def test_cli_resolves_relative_path(tmp_path, monkeypatch):
    from python_scaffolder.cli import main

    monkeypatch.chdir(tmp_path)

    with (
        patch("sys.argv", ["python-scaffolder", "my-project"]),
        patch("python_scaffolder.cli.load_config", return_value={}),
        patch("python_scaffolder.cli.scaffolder.run") as mock_run
    ):
        main()

    expected = (tmp_path / "my-project").resolve()
    mock_run.assert_called_once_with(expected, {})

def test_cli_exists_with_error_on_missing_argument(capsys):
    from python_scaffolder.cli import main

    with patch("sys.argv", ["python-scaffolder"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0
