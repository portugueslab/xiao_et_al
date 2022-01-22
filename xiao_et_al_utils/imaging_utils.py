import numpy as np
from numba import njit, prange
from scipy.signal import detrend


def preprocess_traces(traces_in):
    traces = traces_in.copy()
    samp_n, n_cells = traces.shape
    for i in range(n_cells):
        traces[:, i] = detrend(traces[:, i])
    return (traces - np.nanmean(traces, 0)) / np.nanstd(traces, 0)


@njit
def roll_matrix(input_mat, indexes):
    output_mat = np.empty_like(input_mat)

    for i in prange(output_mat.shape[1]):
        output_mat[:, i] = np.roll(input_mat[:, i], indexes[i])

    return output_mat


def center_on_peak(input_mat):
    """Recenter along the 1st dimension."""
    idxs = -np.argmax(input_mat, 0) - input_mat.shape[0] // 2

    return roll_matrix(input_mat, idxs)
