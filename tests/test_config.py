from unittest.mock import patch

def test_load_config_returns_dict(tmp_path):
    """load_config returns a plain dict when config file exists."""
    from python_scaffolder.config import load_config

    config_file = tmp_path / ".python-scaffolder" / "config.yaml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("git:\n  default_branch: develop\n")

    with patch("python_scaffolder.config.CONFIG_PATH", config_file):
        result = load_config()

    assert isinstance(result, dict)
    assert result["git"]["default_branch"] == "develop"

def test_load_config_creates_default_when_missing(tmp_path):
    """load_config copies the default config when none exists."""
    from python_scaffolder.config import load_config

    config_file = tmp_path / ".python-scaffolder" / "config.yaml"

    with patch("python_scaffolder.config.CONFIG_PATH", config_file):
        result = load_config()

    assert config_file.exists()
    assert isinstance(result, dict)
    # Default config has all five sections
    assert "git" in result
    assert "gitignore" in result
    assert "precommit" in result
    assert "venv" in result
    assert "dotenv" in result

def test_load_config_prints_message_on_bootstrap(tmp_path, capsys):
    """load_config prints an info message when creating the default config."""
    from python_scaffolder.config import load_config

    config_file = tmp_path / ".python-scaffolder" / "config.yaml"

    with patch("python_scaffolder.config.CONFIG_PATH", config_file):
        load_config()

    captured = capsys.readouterr()
    assert str(config_file) in captured.out

def test_get_step_config_returns_subsection():
    """get_step_config returns only the named section."""
    from python_scaffolder.config import get_step_config

    full_config = {"git": {"default_branch": "main"}, "venv": {"packages": ["pre-commit", "pytest"]}}
    assert get_step_config(full_config, "git") == {"default_branch": "main"}

def test_get_step_config_returns_none_when_absent():
    """get_step_config returns None when the section is not in the config."""
    from python_scaffolder.config import get_step_config

    full_config = {"git": {"default_branch": "main"}}
    assert get_step_config(full_config, "precommit") is None
