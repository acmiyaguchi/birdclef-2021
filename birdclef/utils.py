import librosa
import numpy as np
from simple_mp.simple import simple_fast


def simple_fast_self(data, window):
    return simple_fast(data, data, window)


def cens_per_sec(sample_rate, target):
    """Ensure this value is a multiple of 2**6"""
    return (sample_rate // (target * (2 ** 6))) * (2 ** 6)


def compute_offset(index, window_size, cens_total, data_total, window_extra=0):
    """Get the offsets into the original sampled audio by computing the relative
    percentage into the track.

    index: the index into the matrix profile
    window_size: the number of frames used by the matrix profile
    cens_total: the total number of cens frames
    data_total: the total number of audio samples
    window_extra: the number of extra frames to collect from the window
    """
    start = index / (cens_total + window_size)
    end = (index + window_size + window_extra) / (cens_total + window_size)
    offset = (window_size / 2) / (cens_total + window_size)
    return int((start + offset) * data_total), int((end + offset) * data_total)


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


def aligned_slice_indices(n, indices, window):
    # this logic is a bit convoluted, it would be nicer to have an algorithm that's
    # easier to explain
    slices = []
    for start, end in indices:
        if end == -1:
            end = n
        length = end - start
        if length <= window:
            if end < n:
                # get a slice that's centered
                offset = (window - length) // 2
                a = start - offset
                b = a + window
                if a < 0:
                    slices.append((0, window))
                else:
                    slices.append((a, b))
            else:
                # get a slice from the end
                slices.append((n - window, n))
            # don't have to worry about the window being shorter than the actual series
        else:
            # we break this into windows that have no more than 2 slices per window
            slide = int(window * 3 / 4)
            k = int(np.ceil(length / slide))
            total = k * slide
            offset = (total - length) // 2
            for i in range(k):
                a = start - offset + slide * i
                b = a + window
                if a < 0:
                    slices.append((0, window))
                elif b <= n:
                    slices.append((a, b))
                else:
                    # append this offset from the end, and break
                    slices.append((n - window, n))
                    break

    return [x for x in slices if x[1] - x[0] == window]
