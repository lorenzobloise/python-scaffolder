from pathlib import Path

from python_scaffolder.steps.step import Step

class Gitignore(Step):

    @property
    def name(self) -> str:
        return "gitignore"

    def run(self, path: Path, config: dict) -> None:
        """
        Generate .gitignore by concatenating predefined blocks for each section.
        Empty section names are skipped with a warning.
        """
        sections: dict[str, list[str]] = config.get("sections", {})
        lines: list[str] = []
        non_empty_sections: list[str] = []
        for sec in sections:
            blocks: list[str] = sections.get(sec, [])
            if not blocks:
                blocks = []
                self.warn(f"Empty section '{sec}', skipping.")
            lines.extend(blocks)
            if blocks:
                non_empty_sections.append(sec)
        gitignore_path: Path = path / ".gitignore"
        gitignore_path.write_text("\n".join(lines))
        self.success(f"Generated .gitignore (sections: {', '.join(non_empty_sections)})")
