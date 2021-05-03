from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import tensorflow as tf
import tqdm


def reshape_square(arr, k=8):
    """Domain specific. Transform 12x50 matrix into a square matrix that's 25x25."""
    x = np.zeros((12, k * k))
    x[:, : arr.shape[1]] = arr
    return x.reshape(3, 2 * k, 2 * k).T


def cens_per_sec(sample_rate, target):
    """Ensure this value is a multiple of 2**6"""
    return (sample_rate // (target * (2 ** 6))) * (2 ** 6)


def extract_features(path, cens_sr=10):
    data, sample_rate = librosa.load(path)
    cens = librosa.feature.chroma_cens(
        data, sample_rate, hop_length=cens_per_sec(sample_rate, cens_sr)
    )
    # return 5 second slices that are reshaped appropriately
    indexes = np.array(
        [
            np.arange(i, i + 50)
            for i in range(0, cens.shape[1], 50)
            if i + 50 < cens.shape[1]
        ]
    )
    transposed = np.transpose(cens[:, indexes], [1, 0, 2])
    return np.array([reshape_square(x) for x in transposed])


def predict_layer(model, data):
    feature = tf.keras.Model(
        inputs=model.input, outputs=model.get_layer(index=len(model.layers) - 2).output
    )
    return feature.predict(data)


def extract_dataframe(model, site, audio_id, base="../data/input/train_soundscapes"):
    path = list(Path(base).glob(f"{audio_id}_{site}_*.ogg"))
    if not path:
        raise ValueError("audio not found")
    cens = extract_features(path[0])
    feature = predict_layer(model, cens)
    feature_df = pd.DataFrame(feature)
    metadata_df = pd.DataFrame((feature_df.index + 1) * 5, columns=["seconds"])
    metadata_df["site"] = site
    metadata_df["audio_id"] = audio_id
    return metadata_df.join(feature_df)


def main():
    df = pd.read_csv("../data/input/train_soundscape_labels.csv")
    tf.config.set_visible_devices([], "GPU")
    model = tf.keras.models.load_model("../data/models/model-16-16-3-no-mixup-full")
    results = []
    rows = list(df[["site", "audio_id"]].drop_duplicates().itertuples())
    for row in tqdm.tqdm(rows):
        results.append(extract_dataframe(model, row.site, row.audio_id))

    features = pd.concat(results)
    merged = df.merge(features, on=["site", "audio_id", "seconds"])


if __name__ == "__main__":
    main()