"""Remove empty files from the motif folder."""
import shutil
from pathlib import Path

root = Path(__file__).parent.parent / "data"

for path in root.glob("motif/*/*/*"):
    files = list(path.glob("*"))
    if not len(files):
        print(path)
        shutil.rmtree(path)
