def test_cicd_creates_github_pipeline(tmp_path):
    from python_scaffolder.steps.cicd import CICD

    config = {
        "platform": "github",
        "steps": ["lint", "test", "docker"],
    }

    CICD().run(tmp_path, config)

    pipeline_path = tmp_path / ".github" / "workflows" / "ci.yml"
    assert pipeline_path.exists()

    content = pipeline_path.read_text()
    assert "name: CI/CD" in content
    assert "branches:" in content
    assert "- main" in content
    assert "pull_request:" in content
    assert "lint" in content
    assert "test" in content
    assert "docker" in content


def test_cicd_creates_gitlab_pipeline_with_stages(tmp_path):
    from python_scaffolder.steps.cicd import CICD

    config = {
        "platform": "gitlab",
        "steps": ["lint", "test"],
    }

    CICD().run(tmp_path, config)

    pipeline_path = tmp_path / ".gitlab-ci.yml"
    assert pipeline_path.exists()

    content = pipeline_path.read_text()
    assert "stages:" in content
    assert "  - lint" in content
    assert "  - test" in content


def test_cicd_creates_azure_devops_pipeline(tmp_path):
    from python_scaffolder.steps.cicd import CICD

    config = {
        "platform": "devops",
        "steps": ["lint", "test"],
    }

    CICD().run(tmp_path, config)

    pipeline_path = tmp_path / "azure-pipelines.yml"
    assert pipeline_path.exists()

    content = pipeline_path.read_text()
    assert "trigger:" in content
    assert "- main" in content
    assert "pool:" in content
    assert "vmImage: ubuntu-latest" in content
    assert "steps:" in content
    assert "ruff" in content
    assert "pytest" in content


def test_cicd_unsupported_steps_are_skipped(tmp_path, capsys):
    from python_scaffolder.steps.cicd import CICD

    config = {
        "platform": "github",
        "steps": ["lint", "unsupported", "test"],
    }

    CICD().run(tmp_path, config)

    captured = capsys.readouterr()
    assert "Step unsupported not supported. Skipping" in captured.out

    pipeline_path = tmp_path / ".github" / "workflows" / "ci.yml"
    content = pipeline_path.read_text()
    assert "lint" in content
    assert "test" in content
    assert "unsupported" not in content


def test_cicd_empty_steps_creates_pipeline(tmp_path):
    from python_scaffolder.steps.cicd import CICD

    config = {
        "platform": "github",
        "steps": [],
    }

    CICD().run(tmp_path, config)

    pipeline_path = tmp_path / ".github" / "workflows" / "ci.yml"
    assert pipeline_path.exists()

    content = pipeline_path.read_text()
    assert "name: CI/CD" in content
    assert "jobs:" in content


def test_cicd_default_steps_are_empty(tmp_path):
    from python_scaffolder.steps.cicd import CICD

    config = {
        "platform": "gitlab",
    }

    CICD().run(tmp_path, config)

    pipeline_path = tmp_path / ".gitlab-ci.yml"
    assert pipeline_path.exists()

    content = pipeline_path.read_text()
    assert content == "stages:\n\n"


def test_cicd_step_name_is_ci_cd():
    from python_scaffolder.steps.cicd import CICD

    assert CICD().name == "ci-cd"
