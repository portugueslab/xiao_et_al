from pathlib import Path
import numpy as np
from bouter import EmbeddedExperiment
import pandas as pd
from tqdm import tqdm
import flammkuchen as fl
from configparser import ConfigParser

from bouter.utilities import crop, reliability
from xiao_et_al_utils.behavior_and_stimuli import stimulus_df_from_exp0070
from xiao_et_al_utils.imaging import center_on_peak, preprocess_traces

# Data path:
config = ConfigParser()
config.read('param_conf.ini')

master_path = Path(config.get('main', 'data_path'))
# Windows for stimulus cropping for reliability index,
# padding with pre- and post- pause (in seconds):
PRE_INT_S = 2
POST_INT_S = 5

# Windows for computing the average response, in seconds from stim start:
BL_START_S = -2
BL_END_S = 0
RSP_START_S = 0
RSP_END_S = 4

# Microscope pixel size, not logged in metadata:
PX_SIZE = 0.6

# Manually defined offsets for rigid transformation:
all_offsets = fl.load(master_path / "manual_alignment_offsets.h5")

# Abbreviation of genotype from logging:
GEN_ABBR_DICT = {"Huc:H2B-GCaMP6s;olig1:Ntr": "OPC-abl",
                 "Huc:H2B-GCaMP6s": "MTZ-cnt"}

# find all data-containing folders:
path_list = [f.parent for f in master_path.glob("*/data_from_suite2p_unfiltered.h5")]
for path in tqdm(path_list):
    # Load experiment metadata:
    exp = EmbeddedExperiment(path)
    gen_long = exp["general"]["animal"]["genotype"]
    gen = GEN_ABBR_DICT[gen_long]
    fid = path.name

    scanning_meta = exp["imaging"]["microscope_config"]["lightsheet"]["scanning"]
    fs = int(scanning_meta["z"]["frequency"])  # scanning frequency

    # Load, detrend, and Z-score traces
    traces_raw = fl.load(path / "data_from_suite2p_unfiltered.h5", "/traces").T
    traces = preprocess_traces(traces_raw)
    samp_n, n_cells = traces.shape

    # Load stimulus information:
    stim_df = stimulus_df_from_exp0070(exp)
    # Find unique positions in the stimulus:
    unique_stim_pos = sorted(stim_df.loc[:, "pos_start"].unique())
    n_stims = len(unique_stim_pos)

    # Crop around stimuli:
    cropped = crop(traces, stim_df["t"] * fs,
                   pre_int=int(PRE_INT_S * fs), post_int=int(POST_INT_S * fs))
    cropped = cropped - cropped[:int(PRE_INT_S * fs), :, :].mean(0)

    # Loop over positions and compute reliability scores:
    rel_scores = np.zeros((n_stims, n_cells))
    amp_scores = np.zeros((n_stims, n_cells))
    for i, p in enumerate(unique_stim_pos):
        # Find indexes of all repetitions of current stim position:
        resps_idxs = stim_df[stim_df["pos_start"] == p].index

        # Reliability scores, see bouter function
        rel_scores[i] = reliability(cropped[:, resps_idxs, :])

        # Amplitude calculation:
        bl_slice = slice(int((PRE_INT_S + BL_START_S)*fs),
                               int((PRE_INT_S + BL_END_S)*fs))
        rsp_slice = slice(int((PRE_INT_S + RSP_START_S) * fs),
                               int((PRE_INT_S + RSP_END_S) * fs))
        amp_scores[i] = np.nanmean((cropped[rsp_slice, resps_idxs, :].mean(0) -
                          cropped[bl_slice, resps_idxs, :].mean(0)), 0)

    # Compute reliability score centered on the position of max response:
    reord_rel = center_on_peak(rel_scores)

    # Load coords for ROIs and optic tectum mask:
    coords = fl.load(path / "data_from_suite2p_unfiltered.h5", "/coords")
    mask = fl.load(path / "anatomy.mask", "/mask")
    int_c = np.round(coords).astype(np.int)  # convert float coords to integers
    in_tectum = np.array([mask[c[0], c[2], c[1]] for c in int_c]).astype(np.bool)

    # Calculate z step size for the individual fish from Sashimi metadata:
    z_range = scanning_meta["z"]["piezo_max"] - scanning_meta["z"]["piezo_min"]
    n_planes = scanning_meta["triggering"]["n_planes"] - \
        scanning_meta["triggering"]["n_skip_start"]
    z_res = z_range / n_planes

    # Generate pandas DataFrame with scores and centered scores for each cell:
    df = pd.DataFrame(
        np.concatenate([rel_scores, amp_scores, reord_rel], 0).T,
        columns=[f"rel_{i}" for i in range(n_stims)] +
                [f"amp_{i}" for i in range(n_stims)] +
                [f"rel_reord_{i}" for i in range(n_stims)])

    df["cid"] = [f"{fid}_{i:05.0f}" for i in range(n_cells)]  # cell ID
    df["gen"] = gen  # genotype
    df["gen_long"] = gen_long  # genotype
    df["fid"] = fid  # fish ID
    df["in_tectum"] = in_tectum  # if ROI is in tectum
    df["max_rel"] = np.nanmax(rel_scores, 0)  # maximum reliability
    df["max_rel_i"] = np.argmax(rel_scores, 0)  # maximum reliability position
    df["max_amp"] = np.nanmax(amp_scores, 0)  # maximum amplitude

    offsets = all_offsets[path.name]
    coords -= offsets

    df["z"] = coords[:, 0]  # vertical pos, planes
    df["x"] = coords[:, 1]  # a-p pos, pixels
    df["y"] = coords[:, 2]  # l-r pos, pixels

    # rigid coordinate translation using manually defined translations:
    offsets = all_offsets[path.name]
    coords -= offsets
    df["z_trasf"] = coords[:, 0] * z_res  # vertical pos
    df["x_trasf"] = coords[:, 1] * PX_SIZE  # a-p pos, um
    df["y_trasf"] = coords[:, 2] * PX_SIZE  # l-r pos, um

    fl.save(path / "cell_df.h5", df)

# Save for quick loading in cumulative plots:
fl.save(master_path / "stim_pos.h5", unique_stim_pos)
