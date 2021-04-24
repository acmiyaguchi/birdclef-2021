import librosa
import numpy as np


def cens_per_sec(sample_rate, target):
    """Ensure this value is a multiple of 2**6"""
    return (sample_rate // (target * (2 ** 6))) * (2 ** 6)


def compute_offset(index, window_size, cens_total, data_total):
    """Get the offsets into the original sampled audio by computing the relative
    percentage into the track.

    index: the index into the matrix profile
    window_size: the number of frames to keep
    cens_total: the total number of cens frames
    data_total: the total number of audio samples
    """
    start = index / cens_total
    end = (index + window_size) / cens_total
    return int(start * data_total), int(end * data_total)


def get_transition_index(v, offset=0):
    idx = np.where(v[:-1] != v[1:])[0] + 1 + offset
    if v[0]:
        idx = np.append([0], idx)
    if v[-1]:
        idx = np.append(idx, [-1])
    res = []
    for i in range(idx.shape[0] // 2):
        res.append(([idx[2 * i], idx[(2 * i) + 1]]))
    return res
