import numpy as np
from numpy.fft import fft, ifft


def simple_fast(data, query, window_size):
    """Get the matrix profile and profile index of data and a query."""
    if data.shape[1] > data.shape[0]:
        data = data.T
        query = query.T
    if query.shape[1] != data.shape[1]:
        raise ValueError(
            f"incompatible query dimension: {query.shape} against {data.shape}"
        )

    n, dim = query.shape

    matrix_profile_length = data.shape[0] - window_size + 1
    matrix_profile = np.zeros(matrix_profile_length)
    profile_index = np.zeros(matrix_profile_length)

    # compute the first dot-product for the data and query
    X, sumx2 = mass_pre(data, window_size)
    _, z0, _ = mass(X, query[:window_size], n, window_size, dim, sumx2)

    # compute necessary values
    X, sumx2 = mass_pre(query, window_size)

    # compute the first distance profile
    distance_profile, z, sumy2 = mass(X, data[:window_size], n, window_size, dim, sumx2)

    # compute the first distance profile
    idx = np.argmin(distance_profile)
    profile_index[0] = idx
    matrix_profile[0] = distance_profile[idx]

    # compute the rest of the matrix profile
    dropval = data[0]
    nz = z.shape[0]
    for i in range(1, matrix_profile_length):
        subsequence = data[i : i + window_size]
        sumy2 -= dropval ** 2 + subsequence[-1] ** 2
        for j in range(dim):
            z[1:nz, j] = (
                z[: nz - 1, j]
                + query[window_size : window_size + nz - 1, j] * subsequence[-1, j]
                - query[: nz - 1, j] * dropval[j]
            )

        z[0] = z0[i]
        dropval = subsequence[0]

        distance_profile = np.zeros(sumx2.shape[0])
        for j in range(dim):
            distance_profile = distance_profile + sumx2[:, j] - 2 * z[:, j] + sumy2[j]

        idx = np.argmin(distance_profile)
        profile_index[i] = idx
        matrix_profile[i] = distance_profile[idx]

    return matrix_profile, profile_index


def mass_pre(x, m):
    """m is the window size."""
    n, dim = x.shape
    x_mat = np.zeros((2 * n, dim))
    x_mat[:n] = x
    X = fft(x_mat)
    cum_sumx2 = (x ** 2).cumsum(axis=0)
    sumx2 = cum_sumx2[m - 1 : n] - np.append(
        np.zeros((1, dim)), cum_sumx2[: n - m], axis=0
    )
    return X, sumx2


def mass(X, y, n, m, dim, sumx2):
    """Calculate the distance profile using the MASS algorithm.

    X: the fft data
    y: the query data
    n: the number of rows in the query
    m: the sliding window size
    dim: the number of dimensions
    sumx2: the precomputed sum of squares

    returns (dist, z, sumy2)
    where
        dist: the distance profile
        z: the last product
        sumy2: the sum of squared query values
    """

    # computing dot product in O(n log n) time
    y_mat = np.zeros((2 * n, dim))
    y_mat[:m] = y[::-1]
    Y = fft(y_mat)
    Z = X * Y
    z = np.real(ifft(Z)[m - 1 : n])

    # compute y stats O(n)
    sumy2 = (y ** 2).sum(axis=0)

    # compute distances O(n)
    dist = np.zeros(sumx2.shape[0])
    for i in range(dim):
        dist = dist + sumx2[:, i] - 2 * z[:, i] + sumy2[i]
    return dist, z, sumy2