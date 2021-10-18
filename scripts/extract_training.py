import os
from multiprocessing import Pool
from pathlib import Path

import click
import networkx as nx
import numpy as np
import pandas as pd
import tqdm
from scipy.stats import median_abs_deviation
from simple_mp.simple import simple_fast

from birdclef import istarmap
from birdclef.utils import aligned_slice_indices, get_transition_index

ROOT = Path(__file__).parent.parent


def compute_motif(cens, window=50):
    mp, pi = simple_fast(cens, cens, window)
    return mp.argmin()


def compute_affinity(df, window=50, sample=100):
    n = df.shape[0]
    aff = np.zeros((n, n))

    # slow n^2 computation, so we sample...
    if sample is None or n <= sample:
        indices = np.arange(n)
    else:
        # limit the indices we compute to the number of sampled items.
        # Unfortunately this makes the training set non-deterministic (which is
        # probably fine anyhow). Taking the best 5 out of 100 seems good...
        indices = np.random.choice(np.arange(n), sample, replace=False)
    for off, i in enumerate(indices):
        row = df.iloc[i]
        motif = row.cens[:, row.motif : row.motif + window]
        for j in indices[off:]:
            mp, _ = simple_fast(df.iloc[j].cens, motif, window // 2)
            # i wish i could keep each of the matrix profiles...
            aff[i][j] = mp.min()
            aff[j][i] = mp.min()
    return aff


def create_digraph(affinity):
    k = 1.4826
    # there may be large number of 0 elements, ignore them
    masked = np.ma.masked_where(affinity == 0, affinity)
    unmasked = masked[masked.mask == False].reshape(-1).filled(0)
    mad = median_abs_deviation(unmasked)
    zscores = (masked - np.median(unmasked)) / (k * mad)
    dropped = masked * (zscores < 1)
    normed = dropped / dropped.sum()
    return nx.from_numpy_matrix(normed.filled(0), create_using=nx.DiGraph)


def get_reference_motif(df, G, k=5, window=20):
    pr = nx.pagerank(G)
    ranked = sorted([(score, idx) for idx, score in pr.items()])
    best = [idx for _, idx in ranked[-k:]]
    return df.iloc[best].apply(lambda r: r.cens[:, r.motif : r.motif + window], axis=1)


def extract_samples(cens, indices, window=50):
    aligned = aligned_slice_indices(cens.shape[1], indices, window)
    return list(zip([cens[:, i:j] for i, j in aligned], aligned))


def write(input_path, output_path):
    output_path.mkdir(exist_ok=True, parents=True)

    df = pd.read_pickle((input_path / "data.pkl.gz").as_posix())
    df["motif"] = df.cens.apply(compute_motif)

    # create an affinity matrix out of 64 randomly sampled motifs, and choose
    # the top 8 based on the pagerank score
    aff = compute_affinity(df, 64)
    np.save(output_path / "affinity", aff)
    G = create_digraph(aff)
    nx.write_weighted_edgelist(G, (output_path / "edgelist").as_posix())
    motifs = get_reference_motif(df, G, 8)
    motifs.to_pickle(output_path / "motifs.pkl.gz")

    profiles = []
    for full in df.cens:
        row_profiles = []
        for motif in motifs:
            mp, _ = simple_fast(full, motif, 25)
            row_profiles.append(mp)
        profiles.append(row_profiles)

    computed = []
    for row in profiles:
        arr = np.array(row)
        averaged = np.median(arr, axis=0)
        med = np.median(arr)
        computed.append(
            dict(
                profile=averaged,
                median=med,
                indices=get_transition_index(averaged < med, 12),
            )
        )
    computed_df = pd.DataFrame(computed)
    computed_df.to_json(output_path / "averaged_profiles.json", orient="records")

    final = df.join(computed_df)
    final["extracted"] = final.apply(
        lambda x: extract_samples(x.cens, x.indices), axis=1
    )
    exploded = final.explode("extracted")
    exploded = exploded[~exploded.extracted.isnull()]
    exploded["cens_slice"] = exploded.extracted.apply(lambda x: x[0])
    exploded["index"] = exploded.extracted.apply(lambda x: x[1])
    train = exploded[["name", "parent", "cens_slice", "index"]]
    train.to_pickle(output_path / "train.pkl.gz")


@click.command()
@click.option("--parallelism", type=int, default=12)
def main(parallelism):
    rel_root = ROOT / "data/cens/train_short_audio"
    src = rel_root
    dst = Path("data/extract_training_v2")
    dst.mkdir(parents=True, exist_ok=True)

    args = []
    for dirpath, dirnames, filenames in os.walk(src):
        if dirnames:
            continue
        rel_dir = Path(dirpath).relative_to(rel_root)
        output_dir = dst / rel_dir
        if output_dir.exists() and (output_dir / "train.pkl.gz").exists():
            print(f"skipping {output_dir}, already exists")
            continue
        args += [(Path(dirpath), output_dir)]

    with Pool(parallelism) as p:
        for _ in tqdm.tqdm(p.istarmap(write, args), total=len(args)):
            pass


if __name__ == "__main__":
    main()
