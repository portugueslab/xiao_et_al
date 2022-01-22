from pathlib import Path

import flammkuchen as fl
import numpy as np
import seaborn as sns
from bouter import EmbeddedExperiment
from bouter.utilities import crop
from matplotlib import pyplot as plt

sns.set(palette="deep", style="ticks")
cols = sns.color_palette()

from xiao_et_al_utils.defaults import IMAGING_DATA_MASTER_PATH
from xiao_et_al_utils.imaging_utils import preprocess_traces
from xiao_et_al_utils.plotting_utils import save_figure
from xiao_et_al_utils.stimuli_utils import stimulus_df_from_exp0070

PRE_INT_S = 2
POST_INT_S = 5

# parameters for circle of subplots:
ax_w = 0.12
ax_c = (0.5, 0.5)
ax_r = 0.37
n_stims = 36
scaling_percentiles = [1, 99.89]
xlims = (-2, 7)

p_w = 0.22  # side of the central histogram

path = IMAGING_DATA_MASTER_PATH / "210611_f5"

# Load traces and experiment metadata:
print("loading data...")
rois = fl.load(path / "data_from_suite2p_unfiltered.h5", "/rois_stack")
coords = fl.load(path / "data_from_suite2p_unfiltered.h5", "/coords")
ot_mask = fl.load(path / "anatomy.mask", "/mask")
exp = EmbeddedExperiment(path)
cells_df = fl.load(path / "cell_df.h5")

print("preprocessing traces...")
traces = preprocess_traces(
    fl.load(path / "data_from_suite2p_unfiltered.h5", "/traces").T
)

# Read original frequency:
fs = int(
    exp["imaging"]["microscope_config"]["lightsheet"]["scanning"]["z"]["frequency"]
)

stim_df = stimulus_df_from_exp0070(exp)

# Crop around stimuli:
cropped = crop(
    traces,
    stim_df["t"] * fs,
    pre_int=int(PRE_INT_S * fs),
    post_int=int(POST_INT_S * fs),
)
cropped = cropped - cropped[: int(PRE_INT_S * fs), :, :].mean(0)

# Find unique positions in the stimulus:
stim_pos = sorted(stim_df.loc[:, "pos_start"].unique())

rel_scores = cells_df.loc[:, [f"rel_{i}" for i in range(len(stim_pos))]].values.T

print("generating figure...")

fig_b = plt.figure(figsize=(5.5, 3))

m_xpos, m_ypos, xside, yside = 0.1, 0.08, 0.43, 0.84
bounds_lims = [(m_xpos + xside * 1.05 * i, m_ypos, xside, yside) for i in range(2)]

x_time = np.arange(0, cropped.shape[0]) / fs - PRE_INT_S  # time array

for c_n, (i_cell, (xpos, ypos, xside, yside)) in enumerate(
    zip([30, 10818], bounds_lims)
):
    # In random subsampled test data, those indexes are not included in the range:
    if i_cell > coords.shape[0] - 1:
        i_cell = coords.shape[0] - 1
    
    cell_plane = int(coords[i_cell, 0])  # plane in which the cell is found

    # Get percentiles of responses scaling:
    y_low, y_high = [
        np.nanpercentile(cropped[:, :, i_cell], p) for p in scaling_percentiles
    ]

    # Color roi stack with red in location of current ROI
    rois_image = np.ones((rois.shape[1:]) + (3,))
    for c in range(3):
        rois_image[:, :, c][rois[cell_plane, :, :] >= 0] = 0.8
        rois_image[:, :, c][rois[cell_plane, :, :] == i_cell] = cols[3][c]

    # Loop over stimulus positions and plot reps and mean:
    for i, th in enumerate(stim_pos):
        resps_idxs = stim_df[stim_df["pos_start"] == th].index

        plot_th = (np.pi * 2 / n_stims) * i - np.pi + (10 * np.pi / 2) / 360
        x = np.cos(plot_th) * ax_r
        y = -np.sin(plot_th) * ax_r

        ax = fig_b.add_axes(
            (
                xpos + (ax_c[0] - ax_w / 2 + x) * xside,
                ypos + (ax_c[1] - ax_w / 2 + y) * yside,
                ax_w * xside,
                ax_w * yside,
            )
        )

        ax.plot(x_time, cropped[:, resps_idxs, i_cell], lw=0.3, c=(0.4,) * 3)
        ax.plot(x_time, cropped[:, resps_idxs, i_cell].mean(1), lw=1, c=cols[3])

        ax.plot([0, 4], [-1.5, -1.5], c=cols[0], alpha=0.6, lw=1)
        ax.set(xlim=xlims, ylim=(-y_high, y_high))
        ax.axis("off")

    # Add unit bar:
    ax = fig_b.add_axes(
        (
            xpos + (ax_c[0] - ax_w / 2 - 1 / np.sqrt(2) * ax_r) * xside - 0.05,
            ypos + (ax_c[1] - ax_w / 2 - 1 / np.sqrt(2) * ax_r) * yside,
            ax_w * xside,
            ax_w * yside,
        )
    )
    ax.set(xlim=xlims, ylim=(-y_high, y_high))
    bar_pos_x, bar_pos_y = 0, 0
    bar_s_x, bar_s_y = (4, 4)
    ax.axis("off")
    ax.plot(
        [bar_pos_x, bar_pos_x, bar_pos_x + bar_s_x],
        [bar_pos_y + bar_s_y, bar_pos_y, bar_pos_y],
        lw=0.5,
        c=(0.3,) * 3,
    )
    ax.text(
        bar_pos_x - 1,
        bar_pos_y + bar_s_y / 2,
        f"{bar_s_x} dF/F (Z-sc.)",
        ha="right",
        va="center",
        rotation="vertical",
        fontsize=7,
    )
    ax.text(
        bar_pos_x + bar_s_x / 2,
        bar_pos_y - 1,
        f"{bar_s_y} s",
        ha="center",
        va="top",
        fontsize=7,
    )
    ax.patch.set_alpha(0.0)

    # Polar plot:
    ax = fig_b.add_axes(
        (
            xpos + (ax_c[0] - p_w) * xside,
            ypos + (ax_c[1] - p_w) * yside,
            p_w * 2 * xside,
            p_w * 2 * yside,
        ),
        polar=True,
    )

    ax.bar(-np.array(stim_pos), rel_scores[:, i_cell], lw=0, width=np.pi / 18)

    ax.set_thetagrids([])

    ax.spines["polar"].set_visible(False)
    ax.set_ylim(0, 1)
    ax.set_rgrids([0.5, 1], angle=0, fontsize=7)
    ax.text(
        -0.15, 0.85, "Reliability", rotation=0, ha="center", va="center", fontsize=8
    )

    # Anatomy part:
    anatomy_ax = fig_b.add_axes(
        (xpos - 0.12 * xside, ypos + 0.75 * yside, 0.3 * xside, 0.3 * yside)
    )
    anatomy_ax.set_xlim(-5, rois.shape[1])
    anatomy_ax.contour(
        rois[cell_plane, :, :] == i_cell,
        origin="lower",
        levels=[1],
        linewidths=2,
        colors=[cols[3]],
    )
    anatomy_ax.contour(
        ot_mask[cell_plane, :, :],
        origin="lower",
        levels=[1],
        linewidths=0.5,
        colors=[(0.5,) * 3],
    )
    anatomy_ax.axis("off")


save_figure(Path(__file__).stem)
