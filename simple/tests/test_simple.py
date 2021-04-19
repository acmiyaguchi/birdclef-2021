from simple_mp.simple import simple_fast, mass_pre
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent / "resources/birdcall"


def test_mass_pre():
    full = np.genfromtxt(ROOT / "full.cens.csv", delimiter=",")
    X, sumx2 = mass_pre(full, 10)

    ref_X = np.genfromtxt(ROOT / "full.cens.fft.csv", delimiter=",").reshape(X.shape)
    ref_sumx2 = np.genfromtxt(ROOT / "full.cens.sumx2.csv", delimiter=",").reshape(
        sumx2.shape
    )

    assert np.allclose(ref_sumx2, sumx2), "sum squared"
    assert np.allclose(ref_X, np.real(X)), "fft"


def test_simple_fast_ab_join():
    full = np.genfromtxt(ROOT / "full.cens.csv", delimiter=",")
    motif = np.genfromtxt(ROOT / "motif.cens.0.csv", delimiter=",")
    ref_mp = np.genfromtxt(ROOT / "motif.cens.0.mp.csv", delimiter=",")
    ref_pi = np.genfromtxt(ROOT / "motif.cens.0.pi.csv", delimiter=",")
    mp, pi = simple_fast(full, motif, 10)
    assert np.allclose(ref_mp, mp), mp
    assert np.allclose(ref_pi - 1, pi), pi


def test_simple_fast_self_join():
    full = np.genfromtxt(ROOT / "full.cens.csv", delimiter=",")
    ref_mp = np.genfromtxt(ROOT / "full.cens.mp.csv", delimiter=",")
    ref_pi = np.genfromtxt(ROOT / "full.cens.pi.csv", delimiter=",")
    mp, pi = simple_fast(full, full, 50)
    assert np.allclose(ref_mp, mp), mp
    assert np.allclose(ref_pi - 1, pi), pi
