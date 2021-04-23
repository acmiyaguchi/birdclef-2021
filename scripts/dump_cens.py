import os
from multiprocessing import Pool
from pathlib import Path

import click
import librosa
import pandas as pd
import tqdm

from birdclef.utils import cens_per_sec
from birdclef import istarmap

ROOT = Path(__file__).parent.parent


def dump_data(path, cens_sr):
    data, sample_rate = librosa.load(path)
    cens = librosa.feature.chroma_cens(
        data, sample_rate, hop_length=cens_per_sec(sample_rate, cens_sr)
    )
    return data, sample_rate, cens


def write(input_path, output_path, cens_sr):
    paths = list(input_path.glob("*.ogg"))
    if not paths:
        # print(f"no files found in {input_path}")
        return

    # print(f"processing {input_path}")
    output_path.mkdir(exist_ok=True, parents=True)

    dumped = [dump_data(path, cens_sr) for path in paths]

    res = []
    for (data, sample_rate, cens), path in zip(dumped, paths):
        res.append(
            dict(
                name=path.name.replace(".ogg", ""),
                parent=path.parent.name,
                data=data,
                sample_rate=sample_rate,
                seconds=librosa.get_duration(data, sample_rate),
                cens=cens,
                cens_sample_rate=cens_sr,
                path=path.as_posix(),
            )
        )
    df = pd.DataFrame(res)
    df.to_pickle((output_path / "data.pkl.gz").as_posix())


@click.command()
@click.option("--prefix", type=str, help="manual subdirectory to convert")
@click.option("--cens-sr", type=str, default=10, help="Sample rate for CEN data")
@click.option("--parallelism", type=int, default=12)
def main(prefix, cens_sr, parallelism):
    rel_root = ROOT / "data/input"
    src = rel_root
    dst = Path("data/cens")
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
