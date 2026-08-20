from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run_mock(global_user_name="global-user", global_user_email="global@example.com"):
    """Return a mock for subprocess.run that emulates git config get responses."""
    def side_effect(cmd, **kwargs):
        # git config get user.name  →  return the global name
        if cmd == ["git", "config", "get", "user.name"]:
            result = MagicMock()
            result.stdout = global_user_name
            result.stderr = ""
            return result
        # git config get user.email  →  return the global email
        if cmd == ["git", "config", "get", "user.email"]:
            result = MagicMock()
            result.stdout = global_user_email
            result.stderr = ""
            return result
        # Every other git call (init, config set, checkout) returns None
        return None

    mock = MagicMock(side_effect=side_effect)
    return mock


# ---------------------------------------------------------------------------
# git init
# ---------------------------------------------------------------------------

def test_git_runs_init(tmp_path):
    from python_scaffolder.steps.git import Git

    git = Git()

    with patch("python_scaffolder.steps.git.subprocess.run", _make_run_mock()):
        git.run(tmp_path, {"default_branch": "main"})

    # We can't assert directly on the mock here because we passed a fresh
    # callable; use a patched mock below for precise assertions.


def test_git_init_called_with_correct_path(tmp_path):
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"default_branch": "main"})

    init_call = mock_run.call_args_list[0]
    assert init_call.args[0] == ["git", "init", str(tmp_path)]


# ---------------------------------------------------------------------------
# default branch
# ---------------------------------------------------------------------------

def test_git_creates_default_branch(tmp_path):
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"default_branch": "develop"})

    # Find the checkout call for the default branch
    checkout_calls = [
        c for c in mock_run.call_args_list
        if len(c.args[0]) >= 4 and c.args[0][3] == "checkout"
    ]
    assert any("develop" in c.args[0] for c in checkout_calls)


def test_git_defaults_to_main_when_branch_missing(tmp_path):
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {})

    checkout_calls = [
        c for c in mock_run.call_args_list
        if len(c.args[0]) >= 4 and c.args[0][3] == "checkout"
    ]
    assert any("main" in c.args[0] for c in checkout_calls)


# ---------------------------------------------------------------------------
# _git_set_user — reads global git config and applies it to the repo
# ---------------------------------------------------------------------------

def test_git_set_user_reads_global_user_name(tmp_path):
    """_git_set_user must query the global git user.name."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {})

    called_cmds = [c.args[0] for c in mock_run.call_args_list]
    assert ["git", "config", "get", "user.name"] in called_cmds


def test_git_set_user_reads_global_user_email(tmp_path):
    """_git_set_user must query the global git user.email."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {})

    called_cmds = [c.args[0] for c in mock_run.call_args_list]
    assert ["git", "config", "get", "user.email"] in called_cmds


def test_git_set_user_applies_global_name_when_not_in_config(tmp_path):
    """When user.name is absent from config, the global git name is used."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock(global_user_name="global-user")

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {})

    set_name_calls = [
        c for c in mock_run.call_args_list
        if c.args[0][:5] == ["git", "-C", str(tmp_path), "config", "set"]
        and "user.name" in c.args[0]
    ]
    assert set_name_calls, "Expected a 'git config set user.name' call"
    assert set_name_calls[0].args[0][-1] == "global-user"


def test_git_set_user_applies_global_email_when_not_in_config(tmp_path):
    """When user.email is absent from config, the global git email is used."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock(global_user_email="global@example.com")

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {})

    set_email_calls = [
        c for c in mock_run.call_args_list
        if c.args[0][:5] == ["git", "-C", str(tmp_path), "config", "set"]
        and "user.email" in c.args[0]
    ]
    assert set_email_calls, "Expected a 'git config set user.email' call"
    assert set_email_calls[0].args[0][-1] == "global@example.com"


def test_git_set_user_overrides_name_from_config(tmp_path):
    """When user.name is explicitly set in config, it overrides the global value."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock(global_user_name="global-user")

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"user.name": "custom-user"})

    set_name_calls = [
        c for c in mock_run.call_args_list
        if c.args[0][:5] == ["git", "-C", str(tmp_path), "config", "set"]
        and "user.name" in c.args[0]
    ]
    assert set_name_calls, "Expected a 'git config set user.name' call"
    assert set_name_calls[0].args[0][-1] == "custom-user"


def test_git_set_user_overrides_email_from_config(tmp_path):
    """When user.email is explicitly set in config, it overrides the global value."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock(global_user_email="global@example.com")

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"user.email": "custom@example.com"})

    set_email_calls = [
        c for c in mock_run.call_args_list
        if c.args[0][:5] == ["git", "-C", str(tmp_path), "config", "set"]
        and "user.email" in c.args[0]
    ]
    assert set_email_calls, "Expected a 'git config set user.email' call"
    assert set_email_calls[0].args[0][-1] == "custom@example.com"


def test_git_set_user_falls_back_to_stderr_when_stdout_empty(tmp_path):
    """If stdout is empty, _git_set_user falls back to stderr for the global value."""
    from python_scaffolder.steps.git import Git

    git = Git()

    def side_effect(cmd, **kwargs):
        if cmd == ["git", "config", "get", "user.name"]:
            result = MagicMock()
            result.stdout = ""
            result.stderr = "stderr-user"
            return result
        if cmd == ["git", "config", "get", "user.email"]:
            result = MagicMock()
            result.stdout = ""
            result.stderr = "stderr@example.com"
            return result
        return None

    mock_run = MagicMock(side_effect=side_effect)

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {})

    set_name_calls = [
        c for c in mock_run.call_args_list
        if c.args[0][:5] == ["git", "-C", str(tmp_path), "config", "set"]
        and "user.name" in c.args[0]
    ]
    assert set_name_calls[0].args[0][-1] == "stderr-user"


# ---------------------------------------------------------------------------
# _git_create_branches — extra branches
# ---------------------------------------------------------------------------

def test_git_creates_additional_branches(tmp_path):
    """Extra branches listed in config['branches'] must each be checked out."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"default_branch": "main", "branches": ["develop", "staging"]})

    checkout_calls = [
        c.args[0] for c in mock_run.call_args_list
        if len(c.args[0]) >= 4 and c.args[0][3] == "checkout"
    ]
    branch_names = [cmd[-1] for cmd in checkout_calls]
    assert "develop" in branch_names
    assert "staging" in branch_names


def test_git_does_not_recreate_default_branch(tmp_path):
    """The default branch must not appear twice in the checkout calls."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"default_branch": "main", "branches": ["main", "develop"]})

    checkout_calls = [
        c.args[0] for c in mock_run.call_args_list
        if len(c.args[0]) >= 4 and c.args[0][3] == "checkout"
    ]
    branch_names = [cmd[-1] for cmd in checkout_calls]
    assert branch_names.count("main") == 1, (
        "The default branch 'main' must be created exactly once"
    )


def test_git_no_extra_checkouts_when_branches_empty(tmp_path):
    """When branches list is empty, only the default branch is checked out."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"default_branch": "main", "branches": []})

    checkout_calls = [
        c.args[0] for c in mock_run.call_args_list
        if len(c.args[0]) >= 4 and c.args[0][3] == "checkout"
    ]
    assert len(checkout_calls) == 1
    assert checkout_calls[0][-1] == "main"


def test_git_no_extra_checkouts_when_branches_missing(tmp_path):
    """When branches key is absent, only the default branch is checked out."""
    from python_scaffolder.steps.git import Git

    git = Git()
    mock_run = _make_run_mock()

    with patch("python_scaffolder.steps.git.subprocess.run", mock_run):
        git.run(tmp_path, {"default_branch": "main"})

    checkout_calls = [
        c.args[0] for c in mock_run.call_args_list
        if len(c.args[0]) >= 4 and c.args[0][3] == "checkout"
    ]
    assert len(checkout_calls) == 1
