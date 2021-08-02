from bouter import EmbeddedExperiment
import numpy as np
import pandas as pd

from svgpath2mpl import parse_path    
from matplotlib import collections

def stimulus_df_from_exp(exp):
    """Generate dataframe of stimulus trials
    from bouter experiments for the optic tectum responses protocol.
    """
    
    logs = exp["stimulus"]["log"][1::2]
    stim_dicts = []

    # plt.figure()
    for log in logs:
        clip = log["clip_mask"]

        pos_start = np.arctan2(clip[1][1] - 0.5, clip[1][0] - 0.5)
        pos_end = np.arctan2(clip[2][1] - 0.5, clip[2][0] - 0.5)

        stim_dicts.append(dict(t=int(log["t_start"]),
                               pos_start=pos_start,
                               pos_end=pos_end
                            ))

    return pd.DataFrame(stim_dicts)

def despine(ax, sides=["right", "top"], rmticks=True):
    if sides == "all":
        sides = ["right", "top", "left", "bottom"]
    if rmticks:
        if sides == "all":
            ax.set(xticks=[], yticks=[])
        elif "left" in sides:
            ax.set(yticks=[])
        elif "bottom" in sides:
            ax.set(xticks=[])
    [ax.axes.spines[s].set_visible(False) for s in sides]
    
from numba import njit, prange

def fix_fid(cid):
    return "_".join(cid.split("_")[:2])

@njit
def roll_matrix(input_mat, indexes):
    
    output_mat = np.empty_like(input_mat)
    
    for i in prange(output_mat.shape[1]):
        output_mat[:, i] = np.roll(input_mat[:, i], indexes[i])
    
    return output_mat

def center_on_peak(input_mat):
    """Recenter along the 1st dimension.
    """
    idxs = - np.argmax(input_mat, 0) - input_mat.shape[0] // 2
    
    return roll_matrix(input_mat, idxs)

def add_fish(ax, offset=(0, 0), scale=1):
    path_fish = 'm0 0c-13.119 71.131-12.078 130.72-12.078 138.78-5.372 8.506-3.932 18.626-3.264 23.963-6.671 1.112-2.891 4.002-2.891 5.114s-2.224 8.005.445 9.116c-.223 3.113.222 0 0 1.557-.223 1.556-3.558 3.558-2.891 8.227.667 4.67 3.558 10.228 6.226 9.784 2.224 4.892 5.559 4.669 7.56 4.447 2.001-.223 8.672-.445 10.228-6.004 5.115-1.556 5.562-4.002 5.559-6.67-.003-3.341.223-8.45-3.113-12.008 3.336-4.224.667-13.786-3.335-13.786 1.59-8.161-2.446-13.786-3.558-20.679-2.223-34.909-.298-102.74 1.112-141.84'
    path = parse_path(path_fish)
    min_p = np.min(path.vertices, 0)
    path.vertices -= min_p
    f = np.abs(path.vertices[:, 1]).max()*scale
    path.vertices[:, 0] =  path.vertices[:, 0] / f
    path.vertices[:, 1] = path.vertices[:, 1] / f
    
    path.vertices += np.array(offset)

    collection = collections.PathCollection([path],
                                                 linewidths=0,
                                                 facecolors=["#909090"])
    ax.add_artist(collection)