# python-scaffolder

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/py-scaffoldr?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/py-scaffoldr)

A pip-installable CLI tool that scaffolds new Python projects from a YAML configuration file.

## Installation

```bash
pip install py-scaffoldr
```

## Usage

```bash
python-scaffolder my-new-project
python-scaffolder /home/user/projects/my-new-project
```

On install, default config is created at `~/.python-scaffolder/config.yaml`.

## Configuration

Edit `~/.python-scaffolder/config.yaml` to customise your scaffolding.
Comment out an entire section to disable that step.

```yaml
# python-scaffolder configuration
# Comment out an entire top-level section to disable the corresponding scaffolding step

python-version:
  version: "3.13"

git:
  default_branch: main

gitignore:
  sections:
    python:
      - '*__pycache__/'
      - '*.py[cod]'
      - '*.pyo'
      - '*.pyd'
      - '*.egg-info/'
      - 'dist/'
      - 'build/'
      - '*.egg'
      - '.eggs/'
      - '.python-version'
    venv:
      - '*.venv/'
      - '*venv/'
      - '*env/'
    ide:
      - '*.idea/'
      - '*.vscode/'
      - '*.swp'
      - '*.swo'
      - '*.DS_Store'
    env:
      - '*.env'
      - '*.env.*'

precommit:
  repos:
    - id: "pre-commit-hooks"
      repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v5.0.0
      description: "Generic cleanup and config-file checks"
      hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
    - id: "ruff-pre-commit"
      repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.14.7
      description: "Python: lint + formatting (Ruff)"
      hooks:
        - id: ruff-check
          args: ["--fix"]
    - id: "detect-secrets"
      repo: https://github.com/Yelp/detect-secrets
      rev: v1.4.0
      description: "Security: detect secrets"
      hooks:
        - id: detect-secrets
    - id: "bandit"
      repo: https://github.com/PyCQA/bandit
      rev: 1.7.9
      description: "Python security analysis"
      hooks:
        - id: bandit
          args: ["-q", "-ll"]
    - id: ensure-gitignore-vscode
      repo: https://github.com/lorenzobloise/ensure-gitignore-vscode
      rev: v1.0.2
      description: "Ensure .vscode/ in .gitignore file"
      hooks:
        - id: ensure-gitignore-vscode

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

directories:
  directories:
    - <project_dir>
    - docs/
    - tests/

docker:
  digest: null
  entry_point: "main.py"

ci-cd:
  platform: github # {github -> GitHub Actions, gitlab -> GitLab Pipelines, devops -> Azure DevOps Pipelines}
  steps:
    - test
    - docker
```

For new pre-commit hooks, provide `id`, `repo`, `rev` and `hooks` (optionally a `description`):

```yaml
precommit:
  repos:
      - repo: https://github.com/econchick/interrogate
        rev: 1.5.0
        description: "Docstring coverage"
        hooks:
        - id: interrogate
            args: ["--quiet", "--fail-under=70"]
```

## Requirements

- Python 3.10+
- git available on PATH

## Credits

**Lorenzo Bloise**
Developer & Maintainer

- 📧 [l.bloise@outlook.it](mailto:l.bloise@outlook.it)
