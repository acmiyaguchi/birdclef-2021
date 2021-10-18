import os
import sys
from functools import partial
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
import click
import librosa
import soundfile as sf
import tqdm
from pyspark.sql import SparkSession

from birdclef.utils import compute_offset

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

ROOT = Path(__file__).parent.parent


def write(row, output_path):
    if output_path.exists() and not output_path.is_dir():
        raise ValueError("output_path should be a folder")

    path = Path(row.path)
    uid = path.name.split(".")[0]
    species = path.parts[-2]

    if len(list(output_path.glob(f"{species}.{uid}.*.ogg"))) == 2:
        return

    data, sample_rate = librosa.load(path)
    for idx, motif in enumerate([row.motif_0, row.motif_1]):
        i, j = compute_offset(motif, 50, row.duration_cens, row.duration_samples)
        sf.write(
            f"{output_path}/{species}.{uid}.{idx}.ogg",
            data[i:j],
            sample_rate,
            format="ogg",
            subtype="vorbis",
        )


@click.command()
@click.argument("output", type=str)
def main(output):
    # output path is relative to the current directory
    df = pd.read_parquet((ROOT / "data" / "motif_v2").as_posix())

    Path(output).mkdir(exist_ok=True, parents=True)

    with Pool(12) as p:
        list(
            tqdm.tqdm(
                p.imap(partial(write, output_path=Path(output)), df.itertuples()),
                total=(df.shape[0]),
            )
        )


if __name__ == "__main__":
    main()
