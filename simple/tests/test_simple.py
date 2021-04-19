from simple_mp.simple import simple_fast
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent / "resources/birdcall"


def test_simple_fast_ab_join():
    full = np.genfromtxt(ROOT / "full.cens.csv", delimiter=",")
    motif = np.genfromtxt(ROOT / "motif.cens.0.csv", delimiter=",")
    ref_mp = np.genfromtxt(ROOT / "motif.cens.0.mp.csv", delimiter=",")
    ref_pi = np.genfromtxt(ROOT / "motif.cens.0.pi.csv", delimiter=",")
    mp, pi = simple_fast(full, motif, 10)
    assert np.allclose(ref_mp, mp), mp
    assert np.allclose(ref_pi, pi), pi


def test_simple_fast_self_join():
    full = np.genfromtxt(ROOT / "full.cens.csv", delimiter=",")
    ref_mp = np.genfromtxt(ROOT / "full.cens.mp.csv", delimiter=",")
    ref_pi = np.genfromtxt(ROOT / "full.cens.pi.csv", delimiter=",")
    mp, pi = simple_fast(full, full, 50)
    assert np.allclose(ref_mp, mp), mp
    assert np.allclose(ref_pi, pi), pi
