import yaml

def test_precommit_requires_id_repo_rev_and_hooks(tmp_path):
    from python_scaffolder.steps.precommit import Precommit

    config = {
        "repos": [
            {
                "id": "my-custom-hook",
                "repo": "https://github.com/my/repo",
                "rev": "v1.0.0",
                "hooks": [{"id": "my-custom-hook"}]
            }
        ]
    }
    Precommit().run(tmp_path, config)

    precommit_path = tmp_path / ".pre-commit-config.yaml"
    content = yaml.safe_load(precommit_path.read_text())
    repos = content["repos"]
    assert any(r["repo"] == "https://github.com/my/repo" for r in repos)
    assert any(r["rev"] == "v1.0.0" for r in repos)
    assert any(r["hooks"][0]["id"] for r in repos)

def test_precommit_hook_with_empty_fields_is_skipped(tmp_path, capsys):
    from python_scaffolder.steps.precommit import Precommit

    config = {
        "repos": [
            {
                "id": "empty-hook",
                "repo": "https://github.com/my/repo",
                "rev": "v1.0.0"
            },
            {
                "id": "non-empty-hook",
                "repo": "https://github.com/my/repo_2",
                "rev": "v1.0.0",
                "hooks": [{"id": "my-custom-hook"}]
            },
            {
                "id": "empty-hook-2",
                "rev": "v1.0.0",
                "hooks": [{"id": "my-custom-hook"}]
            },
            {
                "id": "empty-hook-3",
                "repo": "https://github.com/my/repo_3",
                "hooks": [{"id": "my-custom-hook"}]
            }
        ]
    }
    Precommit().run(tmp_path, config)

    captured = capsys.readouterr()
    assert "empty-hook" in captured.out
    assert "empty-hook-2" in captured.out
    assert "empty-hook-3" in captured.out
    precommit_path = tmp_path / ".pre-commit-config.yaml"
    content = yaml.safe_load(precommit_path.read_text())
    repos = content["repos"]
    assert all(r["repo"] != "https://github.com/my/repo" for r in repos)
    assert any(r["repo"] == "https://github.com/my/repo_2" for r in repos)

def test_precommit_hook_extra_fields_passed_through(tmp_path):
    from python_scaffolder.steps.precommit import Precommit

    config = {
        "hooks": [
            {
                "id": "black",
                "args": ["--line-length", "100"]
            }
        ]
    }
    config = {
        "repos": [
            {
                "id": "my-custom-hook",
                "repo": "https://github.com/my/repo",
                "rev": "v1.0.0",
                "hooks": [{
                    "id": "my-custom-hook",
                    "args": ["--line-length", "100"],
                    "stages": ["custom-stage"],
                    "additional_dependencies": ["@custom/additional_dependency"]
                }]
            }
        ]
    }
    Precommit().run(tmp_path, config)

    precommit_path = tmp_path / ".pre-commit-config.yaml"
    content: dict = yaml.safe_load(precommit_path.read_text())
    repos: list[dict] = content["repos"]
    all_hooks: list[dict] = [h for repo in repos for h in repo["hooks"]]
    my_custom_hook = next(h for h in all_hooks if h["id"] == "my-custom-hook")
    assert my_custom_hook.get("args") == ["--line-length", "100"]
    assert my_custom_hook.get("stages") == ["custom-stage"]
    assert my_custom_hook.get("additional_dependencies") == ["@custom/additional_dependency"]

def test_precommit_creates_valid_yaml(tmp_path):
    from python_scaffolder.steps.precommit import Precommit

    config = {
        "repos": [
            {
                "id": "my-custom-hook",
                "repo": "https://github.com/my/repo",
                "rev": "v1.0.0",
                "hooks": [{"id": "my-custom-hook"}]
            }
        ]
    }
    Precommit().run(tmp_path, config)

    pc_file = tmp_path / ".pre-commit-config.yaml"
    assert pc_file.exists()
    parsed = yaml.safe_load(pc_file.read_text())
    assert "repos" in parsed

def test_precommit_descriptions_are_only_written_as_comments(tmp_path):
    from python_scaffolder.steps.precommit import Precommit

    description: str = "Description of my custom hook"
    config = {
        "repos": [
            {
                "id": "my-custom-hook",
                "repo": "https://github.com/my/repo",
                "rev": "v1.0.0",
                "description": description,
                "hooks": [{"id": "my-custom-hook"}]
            }
        ]
    }
    Precommit().run(tmp_path, config)

    precommit_path = tmp_path / ".pre-commit-config.yaml"
    text_content = precommit_path.read_text()
    assert f"# {description}\n" in text_content
    content = yaml.safe_load(precommit_path.read_text())
    repos = content["repos"]
    assert all("description" not in r for r in repos)
