from pathlib import Path

def run(path: Path, config: dict) -> None:
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
    print(f"[dotenv]     Generated .env ({len(variables)} variables)")
