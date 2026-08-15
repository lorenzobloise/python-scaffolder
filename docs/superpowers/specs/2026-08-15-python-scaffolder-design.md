# Design Spec: python-scaffolder

**Date:** 2026-08-15  
**Status:** Approved  

---

## Overview

`python-scaffolder` is a pip-installable CLI tool that generates the base structure of a new Python project from a YAML configuration file stored in the user's home directory. Scaffolding steps are opt-in: only sections present in the YAML are executed.

---

## Package structure

```
python-scaffolder/
├── pyproject.toml
├── README.md
└── python_scaffolder/
    ├── __init__.py
    ├── cli.py              # CLI entry point, argument parsing
    ├── config.py           # YAML config loading and default bootstrap
    ├── scaffolder.py       # Orchestrator: runs steps present in the config
    └── steps/
        ├── __init__.py
        ├── git.py          # git init + default branch
        ├── gitignore.py    # .gitignore generation
        ├── precommit.py    # .pre-commit-config.yaml generation
        ├── venv.py         # .venv creation + package installation
        └── dotenv.py       # .env generation
```

---

## Components

### `cli.py`

Entry point registered in `pyproject.toml`. Responsibilities:

- Accepts a single positional argument `<path>` (e.g. `python-scaffolder my-project` or `python-scaffolder /home/user/projects/my-project`)
- Resolves the absolute path of the target
- Checks that the target directory does not already exist — if it does, prints a clear error and exits with a non-zero code
- Loads the config via `config.py`
- Delegates execution to `scaffolder.py`

### `config.py`

Responsibilities:

- Checks whether `~/.python-scaffolder/config.yaml` exists
- If it does not exist, creates the directory and copies the default config file bundled with the package (at `python_scaffolder/default_config.yaml`), then prints an informational message to the user
- Loads the YAML and returns a raw dictionary — no strict validation, for maximum flexibility
- Each step receives only its own sub-section of the config

### `scaffolder.py`

Main orchestrator. Responsibilities:

- Creates the project root directory
- For each available step, checks whether the corresponding section is present in the loaded config
- If the section is present: runs the step
- If the section is absent: logs `Skipping <step>: not configured` and moves on
- If a step raises an exception: logs the error and halts execution (no partial cleanup — the user can see what was created up to that point)

Fixed step execution order:

1. `git`
2. `gitignore`
3. `precommit`
4. `venv`
5. `dotenv`

### `steps/git.py`

- Runs `git init <path>`
- Runs `git checkout -b <default_branch>` (config: `git.default_branch`, default: `main`)

### `steps/gitignore.py`

- Generates `.gitignore` by concatenating predefined blocks per section
- Supported sections: `python`, `venv`, `ide`, `env`
- Blocks are hardcoded strings in the module, not external files
- Unrecognised sections are ignored with a warning

### `steps/precommit.py`

- Generates `.pre-commit-config.yaml` from the hook list in `precommit.hooks`
- Each hook is a dictionary with at least `id`; additional fields (e.g. `args`, `language_version`) are passed through as-is into the generated file
- Well-known hooks (trailing-whitespace, end-of-file-fixer, black, ruff, mypy, etc.) are automatically mapped to their correct repo by the tool
- Unknown hooks require the user to also specify `repo` and `rev` in the YAML

### `steps/venv.py`

- Runs `python -m venv .venv` inside the project directory
- If `venv.packages` is a non-empty list, runs `.venv/bin/pip install <packages>`
- On Windows uses `.venv\Scripts\pip`

### `steps/dotenv.py`

- Generates `.env` from the variables in `dotenv.variables`
- Each variable has `key` (required) and `value` (optional)
- If `value` is absent: writes `KEY=`
- If `value` is present: writes `KEY=value`

---

## Default YAML configuration file

Bundled with the package as `python_scaffolder/default_config.yaml`. Copied to `~/.python-scaffolder/config.yaml` on first run.

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

---

## pyproject.toml

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
```

Runtime dependencies: `pyyaml` only. No heavy transitive dependencies.

---

## Installation and usage

```bash
# Install
pip install git+https://github.com/<org>/python-scaffolder

# Edit config (optional — auto-generated on first run)
nano ~/.python-scaffolder/config.yaml

# Create a new project
python-scaffolder my-new-project
python-scaffolder /home/user/projects/my-new-project
```

---

## Expected output

```
Creating project at /home/user/projects/my-new-project...
[git]        Initialized repository (branch: main)
[gitignore]  Generated .gitignore (sections: python, venv, ide, env)
[precommit]  Generated .pre-commit-config.yaml (4 hooks)
[venv]       Created .venv, installed: pre-commit, pytest
[dotenv]     Generated .env (3 variables)

Done. Project ready at /home/user/projects/my-new-project
```

---

## Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Config location | `~/.python-scaffolder/config.yaml` | Survives package upgrades, easy to find |
| Config bootstrap | Copied on first run | No fragile pip hooks, no extra commands |
| Opt-in steps | Missing section = step skipped | Maximum flexibility without redundant boolean flags |
| Existing directory | Immediate error | Zero risk of accidental overwrite |
| Dependencies | `pyyaml` only | Lightweight package, no unexpected transitive dependencies |
| Config validation | No strict validation | Flexibility for custom configs, clear errors at runtime |
