from pathlib import Path

import flammkuchen as fl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from xiao_et_al_utils.defaults import IMAGING_DATA_MASTER_PATH, REL_SCORE_THR
from xiao_et_al_utils.plotting_utils import add_fish, despine, save_figure

sns.set(palette="deep", style="ticks")
cols = sns.color_palette()


def _shift_90_deg(array):
    out = array + np.pi / 2
    out[out > np.pi] = -np.pi + np.mod(out[out > np.pi], np.pi)
    return out


stim_thetas = np.array(fl.load(IMAGING_DATA_MASTER_PATH / "stim_pos.h5"))
pooled_data = fl.load(IMAGING_DATA_MASTER_PATH / "pooled_dfs.h5", "/all_cells_df")
all_responses = pooled_data.loc[
    :, [f"rel_{i}" for i in range(len(stim_thetas))]
].values.T
all_coords = pooled_data.loc[:, ["z_trasf", "x_trasf", "y_trasf"]].values
all_in_tectum = pooled_data["in_tectum"].values

responsive = all_responses.max(0) > REL_SCORE_THR
all_peaks = np.argmax(all_responses, 0)


fig_c = plt.figure(figsize=(4.5, 2))
m_xpos, m_ypos, xside, yside = 0.05, 0.1, 0.7, 0.7
anat_scatt_size = 1

all_axs = [
    fig_c.add_axes((m_xpos + 0.5 * i * xside, m_ypos, xside, yside)) for i in range(2)
]

spacing = 300
for g_i, g in enumerate(["MTZ-cnt", "OPC-abl"]):
    axs = all_axs[g_i]
    filt = responsive & all_in_tectum & (pooled_data["gen"] == g)
    axs.scatter(
        all_coords[filt, 1],
        all_coords[filt, 2],
        c=_shift_90_deg(stim_thetas[all_peaks[filt]]),
        cmap="twilight_shifted",
        s=anat_scatt_size,
        rasterized=True,
    )
    axs.set_aspect("equal", adjustable="box")
    axs.set_title(g)
    despine(axs, sides="all")

    filt = responsive & all_in_tectum & (pooled_data["gen"] == g)
    axs.scatter(
        all_coords[filt, 1],
        all_coords[filt, 0] - spacing + np.random.rand(sum(filt)) * 14,
        c=_shift_90_deg(stim_thetas[all_peaks[filt]]),
        cmap="twilight_shifted",
        s=anat_scatt_size,
        rasterized=True,
    )

    b_len = 100
    bar_pos_x = -260
    if g_i == 0:
        for labels, bar_pos_y in zip(
            [["caud-rost", "l-r"], ["vent-dors", "l-r"]], [100, 100 - spacing]
        ):
            axs.plot(
                [bar_pos_x, bar_pos_x, bar_pos_x + b_len],
                [bar_pos_y - b_len, bar_pos_y, bar_pos_y],
                lw=0.5,
                c=(0.3,) * 3,
            )
            axs.text(
                bar_pos_x,
                bar_pos_y - b_len / 2,
                labels[0],
                ha="right",
                va="center",
                rotation="vertical",
                fontsize=8,
            )
            axs.text(
                bar_pos_x + b_len / 2,
                bar_pos_y + 10,
                labels[1],
                ha="center",
                va="bottom",
                fontsize=8,
            )
    axs.set(xlim=(-280, 280), ylim=(-400, 150))
val_range = np.linspace(-np.pi, np.pi, 100)
axs = fig_c.add_axes((0.0, 0.35, 0.25, 0.25))
axs.imshow(
    _shift_90_deg(np.angle(val_range[:, None] + 1j * val_range[None, :]).T),
    cmap="twilight_shifted",
    extent=[0, 1, 0, 1],
)
axs.text(0.5, 1.05, "stim. θ", fontsize=7, va="bottom", ha="center")
axs.axis("equal")
axs.axis("off")
add_fish(axs, offset=[0.45, 0.0], scale=1.7)

save_figure(Path(__file__).stem)
