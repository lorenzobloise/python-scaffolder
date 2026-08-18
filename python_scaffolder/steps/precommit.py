from pathlib import Path
import yaml

from python_scaffolder.steps.step import Step, LogLabel

class Precommit(Step):

    @property
    def name(self) -> str:
        return "precommit"

    def run(self, path: Path, config: dict) -> None:
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
                self.log(f"Required fields ({', '.join(absent_fields)}) not present for entry {repo}, skipping.", log_label=LogLabel.WARNING)
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
        self.log(f"Generated .pre-commit-config.yaml ({num_hooks} hooks)", log_label=LogLabel.SUCCESS)

_REQUIRED_FIELDS: list[str] = ["id", "repo", "rev", "hooks"]

def _check_absent_fields(repo: dict) -> list[str]:
    return [f for f in _REQUIRED_FIELDS if f not in repo]
