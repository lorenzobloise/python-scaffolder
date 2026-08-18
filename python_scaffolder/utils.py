from tqdm import tqdm

def _log(msg: str, file=None, start: str="", end: str="\n"):
    tqdm.write(s=f"{start}{msg}", file=file, end=end)
