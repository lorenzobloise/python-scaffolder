from pathlib import Path

def run(path: Path, config: dict) -> None:
    sections: dict[str, list[str]] = config.get("sections", {})
    lines: list[str] = []
    non_empty_sections: list[str] = []
    for sec in sections:
        blocks: list[str] = sections.get(sec, [])
        if not blocks:
            blocks = []
            print(f"[gitignore]  Warning: empty section '{sec}', skipping.")
        lines.extend(blocks)
        if blocks:
            non_empty_sections.append(sec)
    gitignore_path: Path = path / ".gitignore"
    gitignore_path.write_text("\n".join(lines))
    print(f"[gitignore]  Generated .gitignore (sections: {', '.join(non_empty_sections)})")