from abc import ABC, abstractmethod
from pathlib import Path

_NUM_INDENTATIONS: int = 1
_WIDTH: int = 15

class Step(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, path: Path, config: dict) -> None: ...

    def _format_msg(self, msg: str, log_label: str="") -> str:
        current_step_label: str = f"[{self.name}]"
        return f"{current_step_label:<{_WIDTH}}{'  ' * _NUM_INDENTATIONS}{log_label}{msg}"

    def log(self, msg: str) -> None:
        print(self._format_msg(msg))

    def warn(self, msg: str) -> None:
        print(self._format_msg(msg, log_label="Warning: "))

    def error(self, msg: str) -> None:
        print(self._format_msg(msg, log_label="Error: "))

    def success(self, msg: str) -> None:
        print(self._format_msg(msg, log_label="✓ "))
