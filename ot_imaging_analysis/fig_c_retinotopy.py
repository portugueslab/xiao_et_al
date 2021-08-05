from configparser import ConfigParser
from pathlib import Path
from matplotlib import pyplot as plt
import matplotlib
import flammkuchen as fl
import numpy as np
import seaborn as sns
sns.set(palette="deep", style="ticks")
cols = sns.color_palette()

matplotlib.use('qt5agg')

from xiao_et_al_utils.plotting import plot_config, add_fish

plot_config()

# Data path:
config = ConfigParser()
config.read('param_conf.ini')


def main():
    master_path = Path(config.get('main', 'data_path'))

    stim_thetas = np.array(fl.save(master_path / "stim_pos.h5"))
    pooled_data = fl.load(master_path / "pooled_dfs.h5", "/all_cells_df")
    all_responses = pooled_data.loc[:, [i for i in range(len(stim_thetas))]].values.T
    all_coords = pooled_data.loc[:, ["z", "x", "y"]].values
    all_in_tectum = pooled_data["in_tectum"].values

    responsive = all_responses.max(0) > 0.5
    all_peaks = np.argmax(all_responses, 0)

    fig_c = plt.figure(figsize=(7.5, 3))
    m_xpos, m_ypos, xside, yside = 0.2, 0.1, 0.3, 0.35
    anat_scatt_size = 3

    all_axs_top = list(fig_c.add_axes((m_xpos, m_ypos + yside,
                                       xside, yside)))
    all_axs_top.append(fig_c.add_axes((m_xpos, m_ypos,
                                       xside, yside), sharex=all_axs_top[0]))

    all_axs_bot = [fig_c.add_axes((m_xpos + 1.2 * xside, m_ypos + j * yside,
                                   xside, yside), sharex=all_axs_top[j])
                   for j in range(1, -1, -1)]
    all_axs = [all_axs_top, all_axs_bot]
    for g_i, (g, lab) in enumerate(zip(["Huc:H2B-GCaMP6s", "Huc:H2B-GCaMP6s;olig1:Ntr"],
                                       ["Control", "OPC ablated"])):
        axs = all_axs[g_i]

        # Loop over planes, for better overlapping:
        for i in range(all_coords[:, 0].max() + 1):
            filt = responsive & all_in_tectum & (all_coords[:, 0] == i) & (
                        pooled_data["gen"] == g)
            axs[0].scatter(all_coords[filt, 1], all_coords[filt, 2],
                           c=stim_thetas[all_peaks[filt]], cmap="twilight_shifted",
                           s=anat_scatt_size)
        axs[0].set_aspect('equal', adjustable='box')
        axs[0].set(xlim=(-20, 760), ylim=(0, 460))

        axs[0].axis("off")
        axs[0].text(351, 450, lab, fontsize=8, va="bottom", ha="center")

        for i in range(12, 0, -1):
            filt = responsive & all_in_tectum & (pooled_data["gen"] == g) & \
                   (all_coords[:, 2] > i * 50) & (all_coords[:, 2] < (i + 1) * 50)
            axs[1].scatter(all_coords[filt, 1], all_coords[filt, 0] * 15,
                           c=stim_thetas[all_peaks[filt]], cmap="twilight_shifted",
                           s=anat_scatt_size)
        axs[1].set_aspect('equal', adjustable='box')
        axs[0].set(xlim=(-20, 760))  # , ylim=(0, 460))
        axs[1].axis("off")

        # if g_i == 1:
        b_len = 100
        bar_pos_x = 0
        for ax, labels, bar_pos_y in zip(axs, [["caud-rost", "l-r"], ["vent-dors", "l-r"]],
                                         [400, 150]):
            ax.plot([bar_pos_x, bar_pos_x, bar_pos_x + b_len],
                    [bar_pos_y - b_len, bar_pos_y, bar_pos_y], lw=0.5 * g_i, c=(0.3,) * 3)
            if g_i > 0:
                ax.text(bar_pos_x, bar_pos_y - b_len / 2, labels[0], ha="right",
                        va="center",
                        rotation='vertical', fontsize=8)
                ax.text(bar_pos_x + b_len / 2, bar_pos_y + 10, labels[1], ha="center",
                        va="bottom", fontsize=8)

    val_range = np.linspace(-np.pi, np.pi, 100)
    ax = fig_c.add_axes((0., 0.35, 0.25, 0.25))
    ax.imshow(np.angle(val_range[:, None] + 1j * val_range[None, :]).T,
              cmap="twilight_shifted", extent=[0, 1, 0, 1])
    ax.text(0.5, 1.05, "stim. θ", fontsize=7, va="bottom", ha="center")
    ax.axis("equal")
    ax.axis("off")
    add_fish(ax, offset=[0.45, 0.0], scale=1.7)


    fig_c.savefig(Path(config.get('main', 'fig_path')) / "fig_b.pdf")
