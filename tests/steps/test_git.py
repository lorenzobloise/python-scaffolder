from unittest.mock import patch

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
