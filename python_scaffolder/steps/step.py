from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from python_scaffolder.utils import _log

_NUM_INDENTATIONS: int = 1
_WIDTH: int = 15
_CARRIAGE_RETURN_SEQUENCE: str = "\033[1A\r"

class LogLabel(Enum):
    INFO = ""
    WARNING = "Warning: "
    ERROR = "Error: "
    SUCCESS = "✓ "

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

    def log(self, msg: str, log_label: LogLabel=LogLabel.INFO, start: str="") -> None:
        _log(Step._format_msg(msg=msg, step_name=self.name, log_label=log_label.value), start=start)

    def success(self, msg: str) -> None:
        self.log(msg, log_label=LogLabel.SUCCESS, start=_CARRIAGE_RETURN_SEQUENCE)

    def warn(self, msg: str) -> None:
        self.log(msg, log_label=LogLabel.WARNING, start=_CARRIAGE_RETURN_SEQUENCE)

    def error(self, msg: str) -> None:
        self.log(msg, log_label=LogLabel.ERROR, start=_CARRIAGE_RETURN_SEQUENCE)
