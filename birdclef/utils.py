import librosa


def cens_per_sec(sample_rate, target):
    """Ensure this value is a multiple of 2**6"""
    return (sample_rate // (target * (2 ** 6))) * (2 ** 6)


def load_cens(input_ogg, cens_sr=10):
    """Return the cens data for an ogg file."""