from enum import Enum
from importlib.resources import files
from pathlib import Path

from python_scaffolder.steps.step import Step

class Platforms(Enum):
    github = "github"
    gitlab = "gitlab"
    devops = "devops"

_PLATFORM_PATH_MAP: dict[Platforms, str] = {
    Platforms.github.value: ".github/workflows/ci.yml",
    Platforms.gitlab.value: ".gitlab-ci.yml",
    Platforms.devops.value: "azure-pipelines.yml"
}

class Steps(Enum):
    lint = "lint"
    test = "test"
    docker = "docker"

class CICD(Step):

    @property
    def name(self) -> str:
        return "ci-cd"

    def _get_platform(self, config: dict) -> str:
        platform: str | None = config.get("platform", None)
        if not platform:
            self.error("Platform not provided")
            return
        if platform not in [p.value for p in Platforms]:
            self.error(f"Platform {platform} not supported")
            return
        return platform

    def __handle_unsupported_step(self, step: str, steps: list[str]) -> None:
        self.warn(f"Step {step} not supported. Skipping")
        steps.remove(step)

    class Pipeline:

        def __init__(self, platform: str, steps: list[str]):
            super().__init__()
            self.platform = platform
            self.steps = steps

        def _templates_path(self) -> Path:
            return Path(
                files("python_scaffolder")
                .joinpath("assets", "cicd", self.platform)
            )

        def _start(self) -> str:
            if self.platform == Platforms.github.value:
                return """name: CI/CD

on:
  push:
    branches:
      - main
  pull_request:

jobs:
"""
            if self.platform == Platforms.gitlab.value:
                stages_content: str = "\n".join(
                    f"  - {step}" for step in self.steps
                )
                return f"""stages:
{stages_content}
"""
            return """trigger:
  - main

pool:
  vmImage: ubuntu-latest

steps:
"""

        def create_pipeline(self) -> str:
            templates_path: Path = self._templates_path()
            pipeline = self._start()
            for step in self.steps:
                template_path: Path = templates_path / f"{step}.yml"
                pipeline += template_path.read_text()
                if not pipeline.endswith("\n"):
                    pipeline += "\n"
            return pipeline


    def run(self, path: Path, config: dict) -> None:
        platform: str = self._get_platform(config)
        steps: list[str] = config.get("steps", [])
        supported_steps: set[str] = {step.value for step in Steps}
        unsupported_steps: list[str] = [step for step in steps if step not in supported_steps]
        for unsupp_step in unsupported_steps:
            self.__handle_unsupported_step(unsupp_step, steps)
        file_content: str = self.Pipeline(platform, steps).create_pipeline()
        file_path: Path = path / _PLATFORM_PATH_MAP[platform]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_content)
        self.success(f"Created pipeline for platform {platform} with steps: {', '.join(steps)}")
