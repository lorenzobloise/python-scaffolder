from tqdm import tqdm

_CARRIAGE_RETURN_SEQUENCE: str = "\r"
_HIDE_CURSOR: str = "\033[?25l"
_SHOW_CURSOR: str = "\033[?25h"

def _log(msg: str, file=None, start: str="", end: str="\n"):
    tqdm.write(s=f"{start}{msg}", file=file, end=end)

class BusinessException(Exception):
    pass
