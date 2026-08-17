from abc import ABC, abstractmethod
from pathlib import Path

from python_scaffolder.utils import _log

_NUM_INDENTATIONS: int = 1
_WIDTH: int = 15

class Step(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, path: Path, config: dict) -> None: ...

    @classmethod
    def _format_msg(self, msg: str, step_name: str="", log_label: str="") -> str:
        start_label: str = ""
        if step_name:
            current_step_label: str = f"[{step_name}]"
            start_label = f"{current_step_label:<{_WIDTH}}{'  ' * _NUM_INDENTATIONS}"
        return f"{start_label}{log_label}{msg}"

    def log(self, msg: str) -> None:
        _log(Step._format_msg(msg=msg, step_name=self.name))

    def warn(self, msg: str) -> None:
        _log(Step._format_msg(msg=msg, step_name=self.name, log_label="Warning: "))

    def error(self, msg: str) -> None:
        _log(Step._format_msg(msg=msg, step_name=self.name, log_label="Error: "))

    def success(self, msg: str) -> None:
        _log(Step._format_msg(msg=msg, step_name=self.name, log_label="✓ "))
