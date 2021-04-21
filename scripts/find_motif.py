"""Find the motif pair for each training audio clip in a dataset."""
import json
from pathlib import Path
from multiprocessing import Pool

import click
import IPython.display as ipd
import librosa
import numpy as np
import soundfile as sf
import tqdm
from simple_mp.simple import simple_fast

ROOT = Path(__file__).parent.parent


def cens_per_sec(sample_rate, target):
    """Ensure this value is a multiple of 2**6"""
    return (sample_rate // (target * (2 ** 6))) * (2 ** 6)


def get_motif_index(data, window_size):
    mp, pi = simple_fast(data, data, window_size)
    motif = np.argmin(mp)
    return int(motif), int(pi[motif])


def compute_offset(index, window_size, cens_total, data_total):
    a = int((index / cens_total) * data_total)
    b = int(((index + window_size) / cens_total) * data_total)
    return a, b


def write(input_path, output_path, cens_sr=10, mp_window=50):
    if output_path.exists() and not output_path.is_dir():
        raise ValueError("output_path should be a folder")

    # new directory for each set of files
    name = input_path.name.split(".ogg")[0]
    path = Path(output_path) / name
    path.mkdir(exist_ok=True, parents=True)

    data, sample_rate = librosa.load(input_path)
    cens = librosa.feature.chroma_cens(
        data, sample_rate, hop_length=cens_per_sec(sample_rate, cens_sr)
    )
    idx = get_motif_index(cens, mp_window)

    # write out three things: metadata, ogg, and npx data of the cens transformed data
    offsets = []
    np.save(f"{path}/motif.cens", cens)
    for off, x in enumerate(idx):
        i, j = compute_offset(x, mp_window, cens.shape[1], data.shape[0])

        sf.write(
            f"{path}/motif.{off}.ogg",
            data[i:j],
            sample_rate,
            format="ogg",
            subtype="vorbis",
        )
        np.save(f"{path}/motif.cens.{off}", cens[:, x : x + mp_window])
        np.save(f"{path}/motif.{off}", data[i:j])
        offsets += [i, j]

    (path / "metadata.json").write_text(
        json.dumps(
            {
                "source_name": "/".join(input_path.parts[-3:]),
                "cens_sample_rate": cens_sr,
                "matrix_profile_window": mp_window,
                "cens_0": idx[0],
                "cens_1": idx[1],
                "motif_0_i": offsets[0],
                "motif_0_j": offsets[1],
                "motif_1_i": offsets[2],
                "moitif_1_j": offsets[3],
                "sample_rate": sample_rate,
                "duration_seconds": round(
                    librosa.get_duration(y=data, sr=sample_rate), 2
                ),
                "duration_cens": cens.shape[1],
                "duration_samples": data.shape[0],
            },
            indent=2,
        )
        + "\n"
    )
    return ipd.Audio(data[offsets[0] : offsets[1]], rate=sample_rate)


@click.command()
@click.argument("species", type=str)
def main(species):
    rel_root = ROOT / "data/input"
    src = rel_root / "train_short_audio" / species
    dst = Path("data/motif")
    files = list(src.glob("**/*.ogg"))

    args = []
    for path in files:
        rel_dir = path.relative_to(rel_root).parent
        args.append([path, dst / rel_dir, 10, 50])

    with Pool(12) as p:
        p.starmap(write, tqdm.tqdm(args, total=len(args)), chunksize=1)


if __name__ == "__main__":
    main()
