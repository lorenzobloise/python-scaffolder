# python-scaffolder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pip-installable CLI tool that scaffolds new Python projects from a user-editable YAML config file.

**Architecture:** A `python-scaffolder` command delegates to an orchestrator (`scaffolder.py`) which runs only the steps whose sections are present in `~/.python-scaffolder/config.yaml`. Each step is an isolated module with a single `run(path, config)` function. The config file is auto-generated on first run by copying a default bundled with the package.

**Tech Stack:** Python 3.10+, pyyaml, setuptools, pytest, stdlib only (pathlib, subprocess, shutil, sys)

---

## File map

| File | Role |
|---|---|
| `pyproject.toml` | Package metadata, entry point registration, build config |
| `python_scaffolder/__init__.py` | Empty package marker |
| `python_scaffolder/default_config.yaml` | Default config bundled with the package |
| `python_scaffolder/config.py` | Config bootstrap + YAML loading |
| `python_scaffolder/scaffolder.py` | Orchestrator: creates project dir, dispatches steps |
| `python_scaffolder/cli.py` | Argument parsing, path validation, wires config + scaffolder |
| `python_scaffolder/steps/__init__.py` | Empty package marker |
| `python_scaffolder/steps/git.py` | `git init` + default branch |
| `python_scaffolder/steps/gitignore.py` | `.gitignore` generation from named sections |
| `python_scaffolder/steps/precommit.py` | `.pre-commit-config.yaml` generation from hook list |
| `python_scaffolder/steps/venv.py` | `.venv` creation + pip install |
| `python_scaffolder/steps/dotenv.py` | `.env` generation from key/value list |
| `tests/test_config.py` | Tests for config loading and bootstrap |
| `tests/test_scaffolder.py` | Tests for orchestrator step dispatch logic |
| `tests/steps/test_git.py` | Tests for git step |
| `tests/steps/test_gitignore.py` | Tests for gitignore step |
| `tests/steps/test_precommit.py` | Tests for precommit step |
| `tests/steps/test_venv.py` | Tests for venv step |
| `tests/steps/test_dotenv.py` | Tests for dotenv step |
| `tests/test_cli.py` | End-to-end CLI tests |

---

## Task 1: Package scaffold and pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Create: `python_scaffolder/__init__.py`
- Create: `python_scaffolder/steps/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/steps/__init__.py`

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p python_scaffolder/steps tests/steps
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "python-scaffolder"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["pyyaml"]

[project.scripts]
python-scaffolder = "python_scaffolder.cli:main"

[tool.setuptools.package-data]
python_scaffolder = ["default_config.yaml"]
```

Note: `[tool.setuptools.package-data]` ensures `default_config.yaml` is included in the installed package.

- [ ] **Step 3: Create empty `__init__.py` files**

```bash
touch python_scaffolder/__init__.py
touch python_scaffolder/steps/__init__.py
touch tests/__init__.py
touch tests/steps/__init__.py
```

- [ ] **Step 4: Install the package in editable mode**

```bash
pip install -e ".[dev]" 2>/dev/null || pip install -e .
```

Expected: package installs without errors, `python-scaffolder` command is available.

- [ ] **Step 5: Commit**

```bash
git init
git checkout -b main
git add pyproject.toml python_scaffolder/ tests/
git commit -m "chore: initial package scaffold"
```

---

## Task 2: Default config file

**Files:**
- Create: `python_scaffolder/default_config.yaml`

- [ ] **Step 1: Create the default config**

```yaml
# python-scaffolder configuration
# Comment out an entire section to disable that scaffolding step

git:
  default_branch: main

gitignore:
  sections:
    - python
    - venv
    - ide
    - env

precommit:
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: black
    - id: ruff

venv:
  packages:
    - pre-commit
    - pytest

dotenv:
  variables:
    - key: DEBUG
      value: "true"
    - key: LOG_LEVEL
      value: "INFO"
    - key: DATABASE_URL
```

- [ ] **Step 2: Verify setuptools will include it**

```bash
python -c "import importlib.resources; print(list(importlib.resources.files('python_scaffolder').iterdir()))"
```

Expected: output includes `default_config.yaml`.

- [ ] **Step 3: Commit**

```bash
git add python_scaffolder/default_config.yaml
git commit -m "chore: add default config bundle"
```

---

## Task 3: `config.py` — config loading and bootstrap

**Files:**
- Create: `python_scaffolder/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_config.py
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch


def test_load_config_returns_dict(tmp_path):
    """load_config returns a plain dict when config file exists."""
    from python_scaffolder.config import load_config

    config_file = tmp_path / "config.yaml"
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

    full_config = {"git": {"default_branch": "main"}, "venv": {"packages": ["pytest"]}}
    assert get_step_config(full_config, "git") == {"default_branch": "main"}


def test_get_step_config_returns_none_when_absent():
    """get_step_config returns None when the section is not in the config."""
    from python_scaffolder.config import get_step_config

    full_config = {"git": {"default_branch": "main"}}
    assert get_step_config(full_config, "precommit") is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_config.py -v
```

Expected: all 5 tests FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement `config.py`**

```python
# python_scaffolder/config.py
import shutil
import sys
from importlib.resources import files
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".python-scaffolder" / "config.yaml"


def load_config() -> dict:
    """
    Load the user config from CONFIG_PATH.
    If the file does not exist, bootstrap it from the bundled default and
    print an informational message.
    Returns the parsed YAML as a plain dict.
    """
    if not CONFIG_PATH.exists():
        _bootstrap_config()

    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f) or {}


def _bootstrap_config() -> None:
    """Copy the bundled default_config.yaml to CONFIG_PATH."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    default = files("python_scaffolder").joinpath("default_config.yaml")
    with default.open() as src:
        CONFIG_PATH.write_text(src.read())
    print(f"Created default config at {CONFIG_PATH} — edit it to customise your scaffolding.")


def get_step_config(config: dict, step: str) -> dict | None:
    """
    Return the sub-section of config for the given step name, or None if absent.
    A step is considered disabled when its key is missing from the config.
    """
    return config.get(step)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_config.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/config.py tests/test_config.py
git commit -m "feat: config loading and bootstrap"
```

---

## Task 4: `steps/dotenv.py`

**Files:**
- Create: `python_scaffolder/steps/dotenv.py`
- Create: `tests/steps/test_dotenv.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/steps/test_dotenv.py
import pytest
from pathlib import Path


def test_dotenv_writes_key_with_value(tmp_path):
    from python_scaffolder.steps.dotenv import run

    config = {"variables": [{"key": "DEBUG", "value": "true"}]}
    run(tmp_path, config)

    content = (tmp_path / ".env").read_text()
    assert "DEBUG=true" in content


def test_dotenv_writes_key_without_value(tmp_path):
    from python_scaffolder.steps.dotenv import run

    config = {"variables": [{"key": "DATABASE_URL"}]}
    run(tmp_path, config)

    content = (tmp_path / ".env").read_text()
    assert "DATABASE_URL=" in content


def test_dotenv_writes_multiple_variables(tmp_path):
    from python_scaffolder.steps.dotenv import run

    config = {
        "variables": [
            {"key": "DEBUG", "value": "true"},
            {"key": "LOG_LEVEL", "value": "INFO"},
            {"key": "DATABASE_URL"},
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/steps/test_dotenv.py -v
```

Expected: all 4 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `steps/dotenv.py`**

```python
# python_scaffolder/steps/dotenv.py
from pathlib import Path


def run(path: Path, config: dict) -> None:
    """
    Generate a .env file in path from the variables list in config.
    Each variable dict must have 'key'; 'value' is optional.
    Writes KEY=value or KEY= (no value).
    """
    variables = config.get("variables", [])
    lines = []
    for var in variables:
        key = var["key"]
        value = var.get("value", "")
        lines.append(f"{key}={value}")

    env_file = path / ".env"
    env_file.write_text("\n".join(lines))
    print(f"[dotenv]     Generated .env ({len(variables)} variables)")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/steps/test_dotenv.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/steps/dotenv.py tests/steps/test_dotenv.py
git commit -m "feat: dotenv step"
```

---

## Task 5: `steps/gitignore.py`

**Files:**
- Create: `python_scaffolder/steps/gitignore.py`
- Create: `tests/steps/test_gitignore.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/steps/test_gitignore.py
import pytest
from pathlib import Path


def test_gitignore_python_section(tmp_path):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": ["python"]}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "__pycache__" in content
    assert "*.pyc" in content


def test_gitignore_venv_section(tmp_path):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": ["venv"]}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert ".venv" in content


def test_gitignore_ide_section(tmp_path):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": ["ide"]}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert ".idea" in content or ".vscode" in content


def test_gitignore_env_section(tmp_path):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": ["env"]}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert ".env" in content


def test_gitignore_multiple_sections(tmp_path):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": ["python", "venv", "ide", "env"]}
    run(tmp_path, config)

    content = (tmp_path / ".gitignore").read_text()
    assert "__pycache__" in content
    assert ".venv" in content
    assert ".env" in content


def test_gitignore_unknown_section_is_skipped(tmp_path, capsys):
    from python_scaffolder.steps.gitignore import run

    config = {"sections": ["python", "unknown-section"]}
    run(tmp_path, config)

    captured = capsys.readouterr()
    assert "unknown-section" in captured.out
    content = (tmp_path / ".gitignore").read_text()
    assert "__pycache__" in content  # python section still written
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/steps/test_gitignore.py -v
```

Expected: all 6 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `steps/gitignore.py`**

```python
# python_scaffolder/steps/gitignore.py
from pathlib import Path

_BLOCKS: dict[str, str] = {
    "python": """\
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg-info/
dist/
build/
*.egg
.eggs/
""",
    "venv": """\
# Virtual environment
.venv/
venv/
env/
""",
    "ide": """\
# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store
""",
    "env": """\
# Environment variables
.env
.env.*
!.env.example
""",
}


def run(path: Path, config: dict) -> None:
    """
    Generate .gitignore by concatenating predefined blocks for each section.
    Unrecognised section names are skipped with a warning.
    """
    sections = config.get("sections", [])
    parts = []
    used = []

    for section in sections:
        if section not in _BLOCKS:
            print(f"[gitignore]  Warning: unknown section '{section}', skipping.")
            continue
        parts.append(_BLOCKS[section])
        used.append(section)

    (path / ".gitignore").write_text("\n".join(parts))
    print(f"[gitignore]  Generated .gitignore (sections: {', '.join(used)})")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/steps/test_gitignore.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/steps/gitignore.py tests/steps/test_gitignore.py
git commit -m "feat: gitignore step"
```

---

## Task 6: `steps/precommit.py`

**Files:**
- Create: `python_scaffolder/steps/precommit.py`
- Create: `tests/steps/test_precommit.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/steps/test_precommit.py
import pytest
import yaml
from pathlib import Path


def test_precommit_known_hooks_get_correct_repo(tmp_path):
    from python_scaffolder.steps.precommit import run

    config = {"hooks": [{"id": "black"}, {"id": "ruff"}]}
    run(tmp_path, config)

    content = yaml.safe_load((tmp_path / ".pre-commit-config.yaml").read_text())
    repos = {r["repo"] for r in content["repos"]}
    assert any("psf/black" in r for r in repos)
    assert any("astral-sh/ruff" in r or "charliermarsh/ruff" in r for r in repos)


def test_precommit_trailing_whitespace_and_eof(tmp_path):
    from python_scaffolder.steps.precommit import run

    config = {"hooks": [{"id": "trailing-whitespace"}, {"id": "end-of-file-fixer"}]}
    run(tmp_path, config)

    content = yaml.safe_load((tmp_path / ".pre-commit-config.yaml").read_text())
    all_hook_ids = [
        h["id"]
        for repo in content["repos"]
        for h in repo["hooks"]
    ]
    assert "trailing-whitespace" in all_hook_ids
    assert "end-of-file-fixer" in all_hook_ids


def test_precommit_unknown_hook_requires_repo_and_rev(tmp_path):
    from python_scaffolder.steps.precommit import run

    config = {
        "hooks": [
            {
                "id": "my-custom-hook",
                "repo": "https://github.com/my/repo",
                "rev": "v1.0.0",
            }
        ]
    }
    run(tmp_path, config)

    content = yaml.safe_load((tmp_path / ".pre-commit-config.yaml").read_text())
    repos = content["repos"]
    assert any(r["repo"] == "https://github.com/my/repo" for r in repos)


def test_precommit_unknown_hook_without_repo_raises(tmp_path):
    from python_scaffolder.steps.precommit import run

    config = {"hooks": [{"id": "my-custom-hook"}]}
    with pytest.raises(ValueError, match="my-custom-hook"):
        run(tmp_path, config)


def test_precommit_hook_extra_fields_passed_through(tmp_path):
    from python_scaffolder.steps.precommit import run

    config = {"hooks": [{"id": "black", "args": ["--line-length", "100"]}]}
    run(tmp_path, config)

    content = yaml.safe_load((tmp_path / ".pre-commit-config.yaml").read_text())
    all_hooks = [h for repo in content["repos"] for h in repo["hooks"]]
    black_hook = next(h for h in all_hooks if h["id"] == "black")
    assert black_hook.get("args") == ["--line-length", "100"]


def test_precommit_creates_valid_yaml(tmp_path):
    from python_scaffolder.steps.precommit import run

    config = {"hooks": [{"id": "trailing-whitespace"}, {"id": "black"}]}
    run(tmp_path, config)

    pc_file = tmp_path / ".pre-commit-config.yaml"
    assert pc_file.exists()
    parsed = yaml.safe_load(pc_file.read_text())
    assert "repos" in parsed
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/steps/test_precommit.py -v
```

Expected: all 6 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `steps/precommit.py`**

```python
# python_scaffolder/steps/precommit.py
from pathlib import Path

import yaml

# Map from well-known hook id to (repo_url, rev)
_KNOWN_HOOKS: dict[str, tuple[str, str]] = {
    "trailing-whitespace": ("https://github.com/pre-commit/pre-commit-hooks", "v4.6.0"),
    "end-of-file-fixer": ("https://github.com/pre-commit/pre-commit-hooks", "v4.6.0"),
    "check-yaml": ("https://github.com/pre-commit/pre-commit-hooks", "v4.6.0"),
    "check-added-large-files": ("https://github.com/pre-commit/pre-commit-hooks", "v4.6.0"),
    "black": ("https://github.com/psf/black", "24.4.2"),
    "ruff": ("https://github.com/astral-sh/ruff-pre-commit", "v0.4.4"),
    "ruff-format": ("https://github.com/astral-sh/ruff-pre-commit", "v0.4.4"),
    "mypy": ("https://github.com/pre-commit/mirrors-mypy", "v1.10.0"),
    "isort": ("https://github.com/PyCQA/isort", "5.13.2"),
    "flake8": ("https://github.com/PyCQA/flake8", "7.0.0"),
}


def run(path: Path, config: dict) -> None:
    """
    Generate .pre-commit-config.yaml from the hook list in config.
    Well-known hooks are auto-mapped to their repo + rev.
    Unknown hooks must include 'repo' and 'rev' in their definition.
    Multiple hooks sharing the same repo are grouped under a single repos entry.
    """
    hooks = config.get("hooks", [])

    # Group hooks by repo
    repo_map: dict[str, dict] = {}  # repo_url -> {rev, hooks: [...]}

    for hook_def in hooks:
        hook_id = hook_def["id"]
        extra_fields = {k: v for k, v in hook_def.items() if k not in ("id", "repo", "rev")}

        if hook_id in _KNOWN_HOOKS:
            repo_url, rev = _KNOWN_HOOKS[hook_id]
        elif "repo" in hook_def and "rev" in hook_def:
            repo_url = hook_def["repo"]
            rev = hook_def["rev"]
        else:
            raise ValueError(
                f"Hook '{hook_id}' is not a well-known hook. "
                "Please specify 'repo' and 'rev' in your config."
            )

        if repo_url not in repo_map:
            repo_map[repo_url] = {"rev": rev, "hooks": []}

        hook_entry = {"id": hook_id, **extra_fields}
        repo_map[repo_url]["hooks"].append(hook_entry)

    repos = [
        {"repo": url, "rev": data["rev"], "hooks": data["hooks"]}
        for url, data in repo_map.items()
    ]

    content = {"repos": repos}
    (path / ".pre-commit-config.yaml").write_text(yaml.dump(content, default_flow_style=False))
    print(f"[precommit]  Generated .pre-commit-config.yaml ({len(hooks)} hooks)")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/steps/test_precommit.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/steps/precommit.py tests/steps/test_precommit.py
git commit -m "feat: precommit step"
```

---

## Task 7: `steps/venv.py`

**Files:**
- Create: `python_scaffolder/steps/venv.py`
- Create: `tests/steps/test_venv.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/steps/test_venv.py
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, call


def test_venv_creates_venv_directory(tmp_path):
    """run() calls python -m venv .venv inside the project path."""
    from python_scaffolder.steps.venv import run

    with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
        mock_run.return_value = None
        run(tmp_path, {"packages": []})

    venv_call = mock_run.call_args_list[0]
    assert venv_call.args[0] == [sys.executable, "-m", "venv", str(tmp_path / ".venv")]


def test_venv_installs_packages_when_list_non_empty(tmp_path):
    """run() calls pip install for each package when packages list is non-empty."""
    from python_scaffolder.steps.venv import run

    with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
        mock_run.return_value = None
        run(tmp_path, {"packages": ["pytest", "pre-commit"]})

    assert mock_run.call_count == 2
    pip_call = mock_run.call_args_list[1]
    assert "pytest" in pip_call.args[0]
    assert "pre-commit" in pip_call.args[0]


def test_venv_skips_install_when_packages_empty(tmp_path):
    """run() only calls venv creation when packages list is empty."""
    from python_scaffolder.steps.venv import run

    with patch("python_scaffolder.steps.venv.subprocess.run") as mock_run:
        mock_run.return_value = None
        run(tmp_path, {"packages": []})

    assert mock_run.call_count == 1  # only the venv creation call


def test_venv_uses_correct_pip_path_on_posix(tmp_path):
    """run() uses .venv/bin/pip on POSIX systems."""
    from python_scaffolder.steps.venv import _pip_path

    pip = _pip_path(tmp_path)
    # On posix: .venv/bin/pip; on windows: .venv/Scripts/pip
    assert ".venv" in str(pip)
    assert "pip" in str(pip).lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/steps/test_venv.py -v
```

Expected: all 4 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `steps/venv.py`**

```python
# python_scaffolder/steps/venv.py
import subprocess
import sys
from pathlib import Path


def _pip_path(project_path: Path) -> Path:
    """Return the path to pip inside the .venv, cross-platform."""
    if sys.platform == "win32":
        return project_path / ".venv" / "Scripts" / "pip"
    return project_path / ".venv" / "bin" / "pip"


def run(path: Path, config: dict) -> None:
    """
    Create a .venv inside path using the current Python interpreter.
    If config['packages'] is non-empty, install them via the venv's pip.
    """
    venv_path = path / ".venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
    )

    packages = config.get("packages", [])
    if packages:
        pip = _pip_path(path)
        subprocess.run(
            [str(pip), "install"] + packages,
            check=True,
        )
        print(f"[venv]       Created .venv, installed: {', '.join(packages)}")
    else:
        print("[venv]       Created .venv")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/steps/test_venv.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/steps/venv.py tests/steps/test_venv.py
git commit -m "feat: venv step"
```

---

## Task 8: `steps/git.py`

**Files:**
- Create: `python_scaffolder/steps/git.py`
- Create: `tests/steps/test_git.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/steps/test_git.py
import pytest
from pathlib import Path
from unittest.mock import patch, call


def test_git_runs_init(tmp_path):
    from python_scaffolder.steps.git import run

    with patch("python_scaffolder.steps.git.subprocess.run") as mock_run:
        mock_run.return_value = None
        run(tmp_path, {"default_branch": "main"})

    init_call = mock_run.call_args_list[0]
    assert init_call.args[0] == ["git", "init", str(tmp_path)]


def test_git_creates_default_branch(tmp_path):
    from python_scaffolder.steps.git import run

    with patch("python_scaffolder.steps.git.subprocess.run") as mock_run:
        mock_run.return_value = None
        run(tmp_path, {"default_branch": "develop"})

    branch_call = mock_run.call_args_list[1]
    assert branch_call.args[0] == ["git", "-C", str(tmp_path), "checkout", "-b", "develop"]


def test_git_defaults_to_main_when_branch_missing(tmp_path):
    from python_scaffolder.steps.git import run

    with patch("python_scaffolder.steps.git.subprocess.run") as mock_run:
        mock_run.return_value = None
        run(tmp_path, {})

    branch_call = mock_run.call_args_list[1]
    assert "main" in branch_call.args[0]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/steps/test_git.py -v
```

Expected: all 3 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `steps/git.py`**

```python
# python_scaffolder/steps/git.py
import subprocess
from pathlib import Path


def run(path: Path, config: dict) -> None:
    """
    Initialise a git repository at path and check out the configured default branch.
    config['default_branch'] defaults to 'main' if absent.
    """
    branch = config.get("default_branch", "main")

    subprocess.run(["git", "init", str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "checkout", "-b", branch],
        check=True,
    )
    print(f"[git]        Initialized repository (branch: {branch})")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/steps/test_git.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/steps/git.py tests/steps/test_git.py
git commit -m "feat: git step"
```

---

## Task 9: `scaffolder.py` — orchestrator

**Files:**
- Create: `python_scaffolder/scaffolder.py`
- Create: `tests/test_scaffolder.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_scaffolder.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_scaffolder_creates_project_directory(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path = tmp_path / "my-project"
    config = {}  # no steps configured

    run(project_path, config)

    assert project_path.exists()
    assert project_path.is_dir()


def test_scaffolder_runs_step_when_section_present(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path = tmp_path / "my-project"
    config = {"git": {"default_branch": "main"}}

    with patch("python_scaffolder.scaffolder.git.run") as mock_git:
        run(project_path, config)

    mock_git.assert_called_once_with(project_path, {"default_branch": "main"})


def test_scaffolder_skips_step_when_section_absent(tmp_path, capsys):
    from python_scaffolder.scaffolder import run

    project_path = tmp_path / "my-project"
    config = {}  # no git section

    with patch("python_scaffolder.scaffolder.git.run") as mock_git:
        run(project_path, config)

    mock_git.assert_not_called()
    captured = capsys.readouterr()
    assert "Skipping git" in captured.out


def test_scaffolder_runs_all_steps_when_all_configured(tmp_path):
    from python_scaffolder.scaffolder import run

    project_path = tmp_path / "my-project"
    config = {
        "git": {"default_branch": "main"},
        "gitignore": {"sections": ["python"]},
        "precommit": {"hooks": []},
        "venv": {"packages": []},
        "dotenv": {"variables": []},
    }

    with (
        patch("python_scaffolder.scaffolder.git.run") as mock_git,
        patch("python_scaffolder.scaffolder.gitignore.run") as mock_gitignore,
        patch("python_scaffolder.scaffolder.precommit.run") as mock_precommit,
        patch("python_scaffolder.scaffolder.venv.run") as mock_venv,
        patch("python_scaffolder.scaffolder.dotenv.run") as mock_dotenv,
    ):
        run(project_path, config)

    mock_git.assert_called_once()
    mock_gitignore.assert_called_once()
    mock_precommit.assert_called_once()
    mock_venv.assert_called_once()
    mock_dotenv.assert_called_once()


def test_scaffolder_halts_on_step_exception(tmp_path, capsys):
    from python_scaffolder.scaffolder import run

    project_path = tmp_path / "my-project"
    config = {
        "git": {"default_branch": "main"},
        "gitignore": {"sections": ["python"]},
    }

    with (
        patch("python_scaffolder.scaffolder.git.run", side_effect=RuntimeError("git not found")),
        patch("python_scaffolder.scaffolder.gitignore.run") as mock_gitignore,
    ):
        with pytest.raises(RuntimeError, match="git not found"):
            run(project_path, config)

    mock_gitignore.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_scaffolder.py -v
```

Expected: all 5 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `scaffolder.py`**

```python
# python_scaffolder/scaffolder.py
from pathlib import Path

from python_scaffolder.config import get_step_config
from python_scaffolder.steps import dotenv, git, gitignore, precommit, venv

# Steps execute in this fixed order
_STEPS = [
    ("git", git),
    ("gitignore", gitignore),
    ("precommit", precommit),
    ("venv", venv),
    ("dotenv", dotenv),
]


def run(path: Path, config: dict) -> None:
    """
    Create the project directory and run each configured step in order.
    Steps whose section is absent from config are skipped.
    If a step raises, execution halts immediately (no cleanup).
    """
    print(f"Creating project at {path}...")
    path.mkdir(parents=True, exist_ok=False)

    for step_name, step_module in _STEPS:
        step_config = get_step_config(config, step_name)
        if step_config is None:
            print(f"Skipping {step_name}: not configured")
            continue
        step_module.run(path, step_config)

    print(f"\nDone. Project ready at {path}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_scaffolder.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add python_scaffolder/scaffolder.py tests/test_scaffolder.py
git commit -m "feat: scaffolder orchestrator"
```

---

## Task 10: `cli.py` — entry point and end-to-end test

**Files:**
- Create: `python_scaffolder/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli.py
import pytest
import sys
from pathlib import Path
from unittest.mock import patch


def test_cli_errors_when_directory_exists(tmp_path, capsys):
    from python_scaffolder.cli import main

    existing = tmp_path / "existing-project"
    existing.mkdir()

    with patch("sys.argv", ["python-scaffolder", str(existing)]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0
    captured = capsys.readouterr()
    assert "already exists" in captured.out or "already exists" in captured.err


def test_cli_calls_scaffolder_with_resolved_path(tmp_path):
    from python_scaffolder.cli import main

    target = tmp_path / "new-project"

    with (
        patch("sys.argv", ["python-scaffolder", str(target)]),
        patch("python_scaffolder.cli.load_config", return_value={}),
        patch("python_scaffolder.cli.scaffolder.run") as mock_run,
    ):
        main()

    mock_run.assert_called_once_with(target.resolve(), {})


def test_cli_resolves_relative_path(tmp_path, monkeypatch):
    from python_scaffolder.cli import main

    monkeypatch.chdir(tmp_path)

    with (
        patch("sys.argv", ["python-scaffolder", "my-project"]),
        patch("python_scaffolder.cli.load_config", return_value={}),
        patch("python_scaffolder.cli.scaffolder.run") as mock_run,
    ):
        main()

    expected = (tmp_path / "my-project").resolve()
    mock_run.assert_called_once_with(expected, {})


def test_cli_exits_with_error_on_missing_argument(capsys):
    from python_scaffolder.cli import main

    with patch("sys.argv", ["python-scaffolder"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_cli.py -v
```

Expected: all 4 tests FAIL with `ImportError`.

- [ ] **Step 3: Implement `cli.py`**

```python
# python_scaffolder/cli.py
import sys
from pathlib import Path

from python_scaffolder import scaffolder
from python_scaffolder.config import load_config


def main() -> None:
    """
    Entry point for the python-scaffolder CLI.
    Usage: python-scaffolder <path>
    """
    if len(sys.argv) != 2:
        print("Usage: python-scaffolder <path>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1]).resolve()

    if path.exists():
        print(f"Error: directory '{path}' already exists.", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    scaffolder.run(path, config)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cli.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Run the full test suite**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add python_scaffolder/cli.py tests/test_cli.py
git commit -m "feat: CLI entry point"
```

---

## Task 11: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
# python-scaffolder

A pip-installable CLI tool that scaffolds new Python projects from a YAML configuration file.

## Installation

```bash
pip install git+https://github.com/<org>/python-scaffolder
```

## Usage

```bash
python-scaffolder my-new-project
python-scaffolder /home/user/projects/my-new-project
```

On first run, a default config is created at `~/.python-scaffolder/config.yaml`.

## Configuration

Edit `~/.python-scaffolder/config.yaml` to customise your scaffolding.
Comment out an entire section to disable that step.

```yaml
git:
  default_branch: main

gitignore:
  sections:
    - python
    - venv
    - ide
    - env

precommit:
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: black
    - id: ruff

venv:
  packages:
    - pre-commit
    - pytest

dotenv:
  variables:
    - key: DEBUG
      value: "true"
    - key: DATABASE_URL
```

### Supported gitignore sections

`python`, `venv`, `ide`, `env`

### Well-known pre-commit hooks (auto-mapped to their repo)

`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`,
`black`, `ruff`, `ruff-format`, `mypy`, `isort`, `flake8`

For custom hooks, provide `repo` and `rev`:

```yaml
precommit:
  hooks:
    - id: my-hook
      repo: https://github.com/my/repo
      rev: v1.0.0
```

## Requirements

- Python 3.10+
- git available on PATH
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Self-review

**Spec coverage:**
- ✅ git init + configurable default branch → Task 8
- ✅ .gitignore with configurable sections → Task 5
- ✅ pre-commit with configurable hooks → Task 6
- ✅ .venv creation + package installation → Task 7
- ✅ .env with configurable key/value variables → Task 4
- ✅ Config in `~/.python-scaffolder/config.yaml` → Task 3
- ✅ Config auto-bootstrapped on first run → Task 3
- ✅ Steps opt-in via YAML section presence → Task 9
- ✅ Error on existing directory → Task 10
- ✅ Installable via pip + entry point → Task 1
- ✅ `package-data` for bundled config → Task 1

**Placeholder scan:** No TBD, TODO, or vague steps found.

**Type consistency:** `run(path: Path, config: dict)` signature used consistently across all step modules and referenced correctly in `scaffolder.py`.
