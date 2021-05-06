from functools import partial
from multiprocessing import Pool
from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    InputLayer,
    MaxPooling2D,
    Reshape,
    ZeroPadding2D,
)
from tensorflow.keras.metrics import AUC
from tqdm.auto import tqdm

from birdclef.utils import cens_per_sec


def slice_seconds(data, sample_rate, seconds=5, pad_seconds=0):
    # return 2d array of the original data
    n = len(data)
    k = sample_rate * seconds
    pad = sample_rate * pad_seconds
    indexes = np.array(
        [np.arange(i, i + k + pad) for i in range(0, n, k) if i + k + pad <= n]
    )
    indexed = data[indexes]
    return list(zip((np.arange(len(indexed)) + 1) * 5, indexed))


def mixup(df, alpha=0.4):
    shuf = df.sample(frac=1).reset_index(drop=True)
    x1 = np.stack(df.snippet.values)
    x2 = np.stack(shuf.snippet.values)
    y1 = df.y.values
    y2 = shuf.y.values
    a = np.random.beta(alpha, alpha, (x1.shape[0], 1))
    return (a * x1 + (1 - a) * x2, (a.T * y1 + (1 - a.T) * y2).reshape(-1))


def get_compiled_model(input_shape=612, output_shape=1):
    n = input_shape
    k = int(np.ceil(np.sqrt(n)))
    rpad = k ** 2 - n
    model = Sequential()
    model.add(InputLayer(input_shape=input_shape))
    model.add(Reshape((1, n, 1)))
    model.add(ZeroPadding2D(((0, 0), (0, rpad))))
    model.add(Reshape((k, k, 1)))
    model.add(Conv2D(32, (3, 3), activation="relu"))
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(32, activation="relu"))
    model.add(Dense(output_shape, activation="sigmoid"))

    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=["accuracy", AUC(name="auc")],
    )
    return model


def plot_history(history):
    plt.plot(history.history["accuracy"], label="train")
    plt.plot(history.history["val_accuracy"], label="test")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.show()

    plt.plot(history.history["auc"], label="train")
    plt.plot(history.history["val_auc"], label="test")
    plt.xlabel("Epoch")
    plt.ylabel("AUC")
    plt.legend()
    plt.show()

    plt.plot(history.history["loss"], label="train")
    plt.plot(history.history["val_loss"], label="test")
    plt.xlabel("Epoch")
    plt.ylabel("loss")
    plt.legend()
    plt.show()


def main():

    root = Path(__file__).parent.parent

    input_df = pd.read_csv(f"{root}/data/input/train_soundscape_labels.csv")
    cens_df = pd.read_pickle(f"{root}/data/cens/train_soundscapes/data.pkl.gz")

    cens_df["_snippet"] = cens_df[["name", "data", "sample_rate"]].apply(
        lambda x: slice_seconds(x.data, x.sample_rate), axis=1
    )
    exploded = cens_df.explode("_snippet")
    exploded["seconds"] = exploded["_snippet"].apply(lambda x: x[0])
    exploded["snippet"] = exploded["_snippet"].apply(lambda x: x[1])
    exploded["site"] = exploded.name.apply(lambda x: x.split("_")[1])
    exploded["audio_id"] = exploded.name.apply(lambda x: x.split("_")[0]).astype(int)
    tx_df = input_df.merge(exploded, on=["site", "audio_id", "seconds"])
    tx_df["y"] = tx_df.birds.apply(lambda x: 0.0 if x == "nocall" else 1.0)
    tx_df

    X = np.stack(tx_df.snippet.values)
    y = tx_df.y.values

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    for _ in range(4):
        _X, _y = mixup(tx_df)
        X_train = np.append(X_train, _X, axis=0)
        y_train = np.append(y_train, _y)

    sample_rate = 22050
    convert = partial(
        librosa.feature.chroma_cens,
        hop_length=cens_per_sec(sample_rate, 4),
        n_chroma=36,
        win_len_smooth=None,
    )

    n = X_train.shape[0]
    with Pool(10) as p:
        conv = list(tqdm(p.imap(convert, X_train), total=n))
    X_train = np.array(conv).reshape(n, -1)

    n = X_test.shape[0]
    with Pool(10) as p:
        conv = list(tqdm(p.imap(convert, X_test), total=n))
    X_test = np.array(conv).reshape(n, -1)

    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    test_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test))
    model = get_compiled_model(X_train.shape[1])
    history = model.fit(
        train_dataset.batch(32), epochs=50, validation_data=test_dataset.batch(32)
    )
    plot_history(history)

    model.save(f"{root}/data/models/nocall-detector")


if __name__ == "__main__":
    main()
