import os
from multiprocessing import Pool
from pathlib import Path

import click
import librosa
import pandas as pd
import tqdm

from birdclef import istarmap
from birdclef.utils import cens_per_sec

ROOT = Path(__file__).parent.parent


def write(input_path, output_path, cens_sr):
    paths = list(input_path.glob("*.ogg"))
    if not paths:
        return

    output_path.mkdir(exist_ok=True, parents=True)

    res = []
    for path in paths:
        data, sample_rate = librosa.load(path)
        cens = librosa.feature.chroma_cens(
            data, sample_rate, hop_length=cens_per_sec(sample_rate, cens_sr)
        )
        res.append(
            dict(
                name=path.name.replace(".ogg", ""),
                parent=path.parent.name,
                seconds=librosa.get_duration(data, sample_rate),
                cens=cens,
                cens_sample_rate=cens_sr,
                path=path.as_posix(),
            )
        )
    df = pd.DataFrame(res)
    df.to_pickle((output_path / "data.pkl.gz").as_posix())


@click.command()
@click.option("--prefix", type=str, default="cens_v2", help="output directory name")
@click.option("--cens-sr", type=int, default=4, help="Sample rate for CEN data")
@click.option("--parallelism", type=int, default=12)
def main(prefix, cens_sr, parallelism):
    rel_root = ROOT / "data/input"
    src = rel_root
    dst = Path("data") / prefix
    dst.mkdir(parents=True, exist_ok=True)

    args = []
    for dirpath, dirnames, filenames in os.walk(src):
        if dirnames:
            continue
        rel_dir = Path(dirpath).relative_to(rel_root)
        output_dir = dst / rel_dir
        if output_dir.exists() and list(output_dir.glob("*")):
            print(f"skipping {output_dir}, already exists")
            continue
        args += [(Path(dirpath), output_dir, cens_sr)]

    with Pool(parallelism) as p:
        for _ in tqdm.tqdm(p.istarmap(write, args), total=len(args)):
            pass


if __name__ == "__main__":
    main()
