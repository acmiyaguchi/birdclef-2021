import librosa


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
