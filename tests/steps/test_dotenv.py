def test_dotenv_writes_key_with_value(tmp_path):
    from python_scaffolder.steps.dotenv import run

    config = {"variables": [{"key": "DEBUG", "value": "true"}]}
    run(tmp_path, config)

    content = (tmp_path / ".env").read_text()
    assert "DEBUG=true" in content

def test_dotenv_writes_key_without_value(tmp_path):
    from python_scaffolder.steps.dotenv import run

    config = {
        "variables": [
            {"key": "DEBUG", "value": "true"},
            {"key": "LOG_LEVEL", "value": "INFO"},
            {"key": "DATABASE_URL"}
        ]
    }
    run(tmp_path, config)

    content = (tmp_path / ".env").read_text()
    assert "DEBUG=true" in content
    assert "LOG_LEVEL=INFO" in content
    assert "DATABASE_URL=" in content

def test_dotenv_empty_variables_creates_empty_file(tmp_path):
    from python_scaffolder.steps.dotenv import run

    config = {"variables": []}
    run(tmp_path, config)

    assert (tmp_path / ".env").exists()
    assert (tmp_path / ".env").read_text() == ""
