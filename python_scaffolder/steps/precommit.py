from pathlib import Path
import yaml

def run(path: Path, config: dict) -> None:
    """
    Generate .pre-commit-config.yaml from the hook list in config.
    Hooks must include 'id', 'repo', 'rev' and 'hooks' in their definition.
    """
    repos: list[dict] = config.get("repos", [])
    out: str = "repos:\n"
    num_hooks: int = 0
    for repo in repos:
        absent_fields: list[str] = _check_absent_fields(repo)
        if absent_fields:
            print(f"[precommit]  Warning: required fields ({', '.join(absent_fields)}) not present for entry {repo}, skipping.")
            continue # Skip this entry
        num_hooks += len(repo['hooks'])
        description: str | None = repo.pop("description", None)
        if description:
            out += f"  # {description}\n"
        repo_yaml: str = yaml.safe_dump(repo, allow_unicode=True, sort_keys=False, indent=2)
        # Indent all the block under "- "
        lines: list[str] = repo_yaml.rstrip().splitlines()
        out += f"  -  {lines[0]}\n"
        out += "\n".join(f"     {line}" for line in lines[1:])
        out += "\n"
    precommit_path: Path = path / ".pre-commit-config.yaml"
    precommit_path.write_text(out, encoding='utf-8')
    print(f"[precommit]  Generated .pre-commit-config.yaml ({num_hooks} hooks)")

_REQUIRED_FIELDS: list[str] = ["id", "repo", "rev", "hooks"]

def _check_absent_fields(repo: dict) -> list[str]:
    return [f for f in _REQUIRED_FIELDS if f not in repo]
