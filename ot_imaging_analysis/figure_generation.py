from pathlib import Path
import numpy as np
from bouter import EmbeddedExperiment
import pandas as pd
from tqdm import tqdm
import flammkuchen as fl

from matplotlib import pyplot as plt
import seaborn as sns
sns.set(palette="deep", style="ticks")
cols = sns.color_palette()

from scipy.signal import detrend

from bouter.utilities import crop, reliability
from utilities import stimulus_df_from_exp

master_path = Path("/Volumes/Shared/experiments/E0070_receptive_field/v04_flashing_rad_simple")
path_list = [f.parent for f in master_path.glob("*/data_from_suite2p_unfiltered.h5")]

# Load traces and experiment metadata:
path = master_path / "210611_f5"
traces = fl.load(path / "data_from_suite2p_unfiltered.h5", "/traces").T
coords = fl.load(path / "data_from_suite2p_unfiltered.h5", "/coords")
rois = fl.load(path / "data_from_suite2p_unfiltered.h5", "/rois_stack")
mask = fl.load(path / "anatomy.mask", "/mask")

exp = EmbeddedExperiment(path)

# detrend the traces:
for i in tqdm(range(traces.shape[1])):
    traces[:, i] = detrend(traces[:, i])
traces = (traces - np.nanmean(traces, 0)) / np.nanstd(traces, 0)

# Read original frequency:
fs = int(exp["imaging"]["microscope_config"]["lightsheet"]["scanning"]["z"]["frequency"])
samp_n = traces.shape[0]
t_orig = np.arange(traces.shape[0]) / fs


stim_df = stimulus_df_from_exp(exp)

# Crop around stimuli:
n_cells = traces.shape[1]
PRE_INT_S = 2
POST_INT_S = 5
cropped = crop(traces, stim_df["t"]*fs,
                     pre_int=int(PRE_INT_S*fs), post_int=int(POST_INT_S*fs))
cropped = cropped - cropped[:int(PRE_INT_S*fs), :, :].mean(0)

# Find unique positions in the stimulus:
pos = sorted(stim_df.loc[:, "pos_start"].unique())

# Loop over positions and compute reliability scores:
rel_scores = np.zeros((len(pos), n_cells))

for i, p in tqdm(list(enumerate(pos))):
    resps_idxs = stim_df[stim_df["pos_start"] == p].index

    rel_scores[i] = reliability(cropped[:, resps_idxs, :])