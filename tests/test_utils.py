import json


# --- _get_python_interpreter ---

def test_get_python_interpreter_returns_none_when_cache_file_does_not_exist(tmp_path):
    from python_scaffolder.utils import _get_python_interpreter

    cache_path = tmp_path / "python_interpreters"

    result = _get_python_interpreter("3.13.7", cache_path=cache_path)

    assert result is None


def test_get_python_interpreter_returns_path_when_version_matches(tmp_path):
    from python_scaffolder.utils import _get_python_interpreter

    cache_path = tmp_path / "python_interpreters"
    cache_path.write_text(json.dumps([
        {"version": "3.13.7", "path": "/usr/bin/python3.13"},
        {"version": "3.11.9", "path": "/usr/bin/python3.11"},
    ]))

    result = _get_python_interpreter("3.13.7", cache_path=cache_path)

    assert result == "/usr/bin/python3.13"


def test_get_python_interpreter_returns_none_when_version_not_in_cache(tmp_path):
    from python_scaffolder.utils import _get_python_interpreter

    cache_path = tmp_path / "python_interpreters"
    cache_path.write_text(json.dumps([
        {"version": "3.11.9", "path": "/usr/bin/python3.11"},
    ]))

    result = _get_python_interpreter("3.13.7", cache_path=cache_path)

    assert result is None


def test_get_python_interpreter_returns_none_on_empty_cache(tmp_path):
    from python_scaffolder.utils import _get_python_interpreter

    cache_path = tmp_path / "python_interpreters"
    cache_path.write_text(json.dumps([]))

    result = _get_python_interpreter("3.13.7", cache_path=cache_path)

    assert result is None


def test_get_python_interpreter_does_not_match_by_prefix(tmp_path):
    from python_scaffolder.utils import _get_python_interpreter

    cache_path = tmp_path / "python_interpreters"
    cache_path.write_text(json.dumps([
        {"version": "3.13.7", "path": "/usr/bin/python3.13"},
    ]))

    # "3.13" must not match "3.13.7"
    result = _get_python_interpreter("3.13", cache_path=cache_path)

    assert result is None


def test_get_python_interpreter_returns_first_match_when_duplicates_in_cache(tmp_path):
    from python_scaffolder.utils import _get_python_interpreter

    cache_path = tmp_path / "python_interpreters"
    cache_path.write_text(json.dumps([
        {"version": "3.13.7", "path": "/usr/bin/python3.13"},
        {"version": "3.13.7", "path": "/usr/local/bin/python3.13"},
    ]))

    result = _get_python_interpreter("3.13.7", cache_path=cache_path)

    assert result == "/usr/bin/python3.13"
