import numpy as np
from pathlib import Path

for path in (Path(__file__).parent / "birdcall").glob("*.npy"):
    print(path)
    x = np.load(path)
    np.savetxt(path.as_posix().replace(".npy", ".csv"), x, delimiter=",")
