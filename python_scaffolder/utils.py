from tqdm import tqdm

def _log(msg: str, file=None, end: str="\n"):
    tqdm.write(s=msg, file=file, end=end)
