from abc import ABC, abstractmethod
from pathlib import Path

class Step(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, path: Path, config: dict) -> None: ...

    def log(self, msg: str) -> None:
        print(f"[{self.name}]  {msg}")

    def warn(self, msg: str) -> None:
        print(f"[{self.name}]  Warning: {msg}")

    def error(self, msg: str) -> None:
        print(f"[{self.name}]  Error: {msg}")

    def success(self, msg: str) -> None:
        print(f"[{self.name}]  ✓ {msg}")
