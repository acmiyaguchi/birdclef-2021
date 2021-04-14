"""Remove empty files from the motif folder."""
from pathlib import Path
import shutil

root = Path(__file__).parent.parent / "data"

for path in root.glob("motif/*/*/*"):
    files = list(path.glob("*"))
    if not len(files):
        print(path)
        shutil.rmtree(path)
