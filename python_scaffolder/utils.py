from tqdm import tqdm

def _log(msg: str, file=None):
    tqdm.write(s=msg, file=file)
