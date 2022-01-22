from pathlib import Path

import flammkuchen as fl
import numpy as np
import seaborn as sns
from bouter import EmbeddedExperiment
from matplotlib import pyplot as plt

from xiao_et_al_utils.defaults import IMAGING_DATA_MASTER_PATH
from xiao_et_al_utils.plotting_utils import add_fish, despine, save_figure

sns.set(palette="deep", style="ticks")
cols = sns.color_palette()

path = IMAGING_DATA_MASTER_PATH / "210611_f5"

# Load traces and experiment metadata:
print("loading data...")
anatomy = fl.load(path / "data_from_suite2p_unfiltered.h5", "/anatomy_stack")
ot_mask = fl.load(path / "anatomy.mask", "/mask")
exp = EmbeddedExperiment(path)

print("generating figure...")

fig_a = plt.figure(figsize=(2.5, 3))

xpos, ypos, side = 0.1, 0.7, 0.16
axs = [fig_a.add_axes((xpos + side * 1.1 * i, ypos, side, side)) for i in range(5)]

clip_masks = [s["clip_mask"] for s in exp["stimulus"]["log"][1::2]]
titles = ["4 s", "2 s", "4 s", "2 s", "4 s"]
stimuli = [0, None, 20, None, 10]
for ax, title, stim_n in zip(axs, titles, stimuli):
    ax.fill([0, 1, 1, 0], [0, 0, 1, 1], fc="r")

    if stim_n is not None:
        mask = clip_masks[stim_n]
        ax.fill([m[0] for m in mask], [m[1] for m in mask], fc="k", lw=0, alpha=0.6)
    ax.set(ylim=(0.1, 0.9), xlim=(0.1, 0.9), xticks=[], yticks=[], title=title)
    ax.set_aspect("equal", adjustable="box")

    add_fish(ax, offset=[0.45, 0.08], scale=(30 / 15))

    despine(ax, sides="all")

planes = [2, 6]
pad = 10

an_ax = fig_a.add_axes((0, 0.1, 1, 0.5))
an_ax.imshow(
    np.concatenate([anatomy[i, pad:-pad, pad:-pad] for i in planes]).T,
    cmap="gray_r",
    origin="lower",
    vmax=100,
    vmin=0,
)
an_ax.contour(
    np.concatenate([ot_mask[i, pad:-pad, pad:-pad] for i in planes], axis=1),
    origin="lower",
    levels=[1],
    linewidths=0.5,
    colors=[cols[3]],
)

b_len = 100
bar_pos_x = anatomy.shape[1]
for ax, labels, bar_pos_y in zip(axs, [["caud-rost", "l-r"], ["vent-dors"]], [400]):
    an_ax.plot(
        [bar_pos_x, bar_pos_x, bar_pos_x + b_len],
        [bar_pos_y - b_len, bar_pos_y, bar_pos_y],
        lw=0.5,
        c=(0.3,) * 3,
    )
    an_ax.text(
        bar_pos_x,
        bar_pos_y - b_len / 2,
        labels[0],
        ha="right",
        va="center",
        rotation="vertical",
        fontsize=8,
    )
    an_ax.text(
        bar_pos_x + b_len / 2,
        bar_pos_y + 10,
        labels[1],
        ha="center",
        va="bottom",
        fontsize=8,
    )
an_ax.text(
    anatomy.shape[1] * 2 - pad * 5,
    anatomy.shape[1] - pad * 7,
    "Huc:H2B-GCaMP6s",
    fontsize=7,
    ha="right",
    va="top",
    c=(0.5,) * 3,
)

despine(an_ax, sides="all")

save_figure(Path(__file__).stem)
