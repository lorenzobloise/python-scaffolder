from pathlib import Path

from python_scaffolder.steps.step import Step, LogLabel

class Dotenv(Step):

    @property
    def name(self) -> str:
        return "dotenv"

    def run(self, path: Path, config: dict) -> None:
        """
        Generate a .env file in path from the variables list in config.
        Each variable dict must have 'key'; 'value' is optional.
        Writes KEY=value or KEY= (no value).
        """
        variables: list[dict] = config.get("variables", [])
        lines: list[str] = []
        for var in variables:
            key: str = var["key"]
            value: str = var.get("value", "")
            lines.append(f"{key}={value}\n")
        env_file: Path = path / ".env"
        env_file.write_text("\n".join(lines))
        self.log(f"Generated .env ({len(variables)} variables)", log_label=LogLabel.SUCCESS)
