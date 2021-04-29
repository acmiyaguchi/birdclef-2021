import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Softmax, Flatten, Dense
from pathlib import Path
import datetime


def reshape_square(arr, k=8):
    """Domain specific. Transform 12x50 matrix into a square matrix that's 25x25."""
    x = np.zeros((12, k * k))
    x[:, : arr.shape[1]] = arr
    return x.reshape(3, 2 * k, 2 * k).T


def _mixup(x_in, y_in):
    n = x_in.shape[0]
    # draw from uniform instead of beta(alpha, alpha, BATCH_SIZE)
    w = np.random.uniform(0.3, 0.7, size=n)
    x_weight = w.reshape(n, 1, 1, 1)
    index = np.random.permutation(n)

    x = x_in * x_weight + x_in[index] * (1 - x_weight)
    y = y_in + y_in[index]
    return x, y


@tf.function(
    input_signature=[
        tf.TensorSpec(None, tf.float64),
        tf.TensorSpec(None, tf.int32),
    ]
)
def mixup(x_in, y_in):
    x, y = tf.numpy_function(_mixup, [x_in, y_in], [tf.float64, tf.int32])
    return tf.data.Dataset.from_tensor_slices(
        (tf.reshape(x, [-1, 16, 16, 3]), tf.reshape(y, [-1, 397]))
    )


def add_mixup(dataset, batch_size=1024):
    return (
        dataset.shuffle(batch_size)
        .window(batch_size)
        .flat_map(
            lambda x, y: tf.data.Dataset.zip((x.batch(batch_size), y.batch(batch_size)))
        )
        .map(mixup, num_parallel_calls=tf.data.AUTOTUNE)
        .flat_map(lambda x: x)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )


def get_compiled_model(input_shape=(16, 16, 3), output_shape=397):
    model = Sequential()
    model.add(
        Conv2D(
            32,
            (3, 3),
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
            input_shape=input_shape,
        )
    )
    model.add(
        Conv2D(
            32,
            (3, 3),
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )
    )
    model.add(MaxPooling2D((2, 2)))
    model.add(
        Conv2D(
            64,
            (3, 3),
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )
    )
    model.add(
        Conv2D(
            64,
            (3, 3),
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )
    )
    model.add(MaxPooling2D((2, 2)))
    model.add(
        Conv2D(
            128,
            (3, 3),
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )
    )
    model.add(
        Conv2D(
            128,
            (3, 3),
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )
    )
    model.add(MaxPooling2D((2, 2)))

    model.add(Flatten())
    model.add(Dense(128, activation="relu", kernel_initializer="he_uniform"))
    model.add(Dense(output_shape, activation="sigmoid"))

    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    return model


def main():

    root = Path(__file__).parent.parent

    train_df = pd.read_pickle(f"{root}/data/train_cens.pkl.gz")

    X = np.stack(train_df.cens_slice.apply(reshape_square))

    lb = LabelBinarizer()
    lb.fit(train_df.parent)
    y = lb.transform(train_df.parent)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=1
    )

    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    test_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test))

    model = get_compiled_model()

    logdir = (
        root
        / "data"
        / "logs"
        / "train_cnn"
        / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    )
    tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)

    history = model.fit(
        train_dataset.batch(256),
        epochs=20,
        validation_data=test_dataset.batch(256),
        callbacks=[tensorboard_callback],
    )

    model.save(f"{root}/data/models/model-16-16-3-no-mixup-full")


if __name__ == "__main__":
    main()
