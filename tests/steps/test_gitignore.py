def test_gitignore_python_section(tmp_path):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": {"python": ["*__pycache__/", "*.pyc"]}}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "*__pycache__/" in content
    assert "*.pyc" in content

def test_gitignore_venv_section(tmp_path):
    from python_scaffolder.steps.gitignore import run
    
    config = {"sections": {"venv": ["*.venv/"]}}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "*.venv/" in content

def test_gitignore_ide_section(tmp_path):
    from python_scaffolder.steps.gitignore import run
    
    config = {"sections": {"ide": ["*.idea/", "*.vscode/"]}}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "*.idea/" in content
    assert "*.vscode/" in content

def test_gitignore_env_section(tmp_path):
    from python_scaffolder.steps.gitignore import run
    
    config = {"sections": {"env": ["*.env"]}}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "*.env" in content

def test_gitignore_multiple_sections(tmp_path):
    from python_scaffolder.steps.gitignore import run
        
    config = {
        "sections": {
            "python": ["*__pycache__/"], 
            "venv": ["*.venv/"], 
            "ide": ["*.vscode/"], 
            "env": ["*.env"]
        }
    }
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "*__pycache__/" in content
    assert "*.venv/" in content
    assert "*.vscode/" in content
    assert "*.env" in content

def test_gitignore_empty_section_is_skipped(tmp_path, capsys):
    from python_scaffolder.steps.gitignore import run
            
    config = {
        "sections": {
            "empty-section": None, 
            "python": ["*__pycache__/"]
        }
    }
    run(tmp_path, config)

    captured = capsys.readouterr()
    assert "empty-section" in captured.out
    content = (tmp_path / ".gitignore").read_text()
    assert "*__pycache__/" in content