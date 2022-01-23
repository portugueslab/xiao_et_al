from pathlib import Path

import flammkuchen as fl
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

from xiao_et_al_utils.defaults import (
    DEMO_MODE,
    IMAGING_DATA_MASTER_PATH,
    REL_SCORE_THR,
)
from xiao_et_al_utils.plotting_utils import despine, save_figure


def gaussian(x, a, x0, sigma):
    return a * np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))


def _conv_to_dist(val):
    return (val - 18) * 10


sns.set(palette="deep", style="ticks")
cols = sns.color_palette()

pooled_data_df = fl.load(IMAGING_DATA_MASTER_PATH / "pooled_dfs.h5", "/all_cells_df")
stim_thetas = np.array(fl.load(IMAGING_DATA_MASTER_PATH / "stim_pos.h5"))
n_pos = len(stim_thetas)


# Get nice example to plot
x = np.arange(n_pos)

# Low number if we are just running demo mode with a few cells:
example_thr = 0.5 if DEMO_MODE else 0.9
y_single_neuron = pooled_data_df.loc[
    (pooled_data_df["gen"] == "MTZ-cnt") & (pooled_data_df["max_rel"] > example_thr),
    [f"rel_reord_{i}" for i in range(n_pos)],
].values[0, :]

mean = sum(x * y_single_neuron) / sum(y_single_neuron)
sigma = np.sqrt(sum(y_single_neuron * (x - mean) ** 2) / sum(y_single_neuron))

popt_singleneuron, pcov = curve_fit(
    gaussian, x, y_single_neuron, p0=[max(y_single_neuron), mean, sigma]
)

x_range = _conv_to_dist(np.arange(n_pos))

m_xpos, m_ypos, xside, yside = 0.3, 0.25, 0.6, 0.3

def generate_figure():
    fig_f = plt.figure(figsize=(2, 2))
    axs = [
        fig_f.add_axes((m_xpos, m_ypos + +1.2 * i * yside, xside, yside)) for i in range(2)
    ]

    data = pooled_data_df.loc[
        (pooled_data_df["max_rel"] > REL_SCORE_THR) & pooled_data_df["in_tectum"],
        [f"rel_reord_{i}" for i in range(36)],
    ].values.T
    data = data / data[18, :]
    axs[1].plot(x_range, data[:, ::10], lw=0.3, c=(0.8,) * 3, rasterized=True)

    axs[1].plot(x_range, np.nanmedian(data, 1), lw=2, c=(0.5,) * 3)

    axs[0].plot(
        x_range, y_single_neuron, "o", label="data", lw=1, c=(0.5,) * 3, markersize=3
    )
    axs[0].plot(
        x_range,
        gaussian(np.arange(len(x_range)), *popt_singleneuron),
        "r-",
        label="fit",
        lw=1,
    )
    axs[0].axvspan(
        _conv_to_dist(popt_singleneuron[1] - popt_singleneuron[2]),
        _conv_to_dist(popt_singleneuron[1] + popt_singleneuron[2]),
        fc=(0.9,) * 3,
        lw=0,
    )
    axs[0].text(
        _conv_to_dist(popt_singleneuron[1]),
        1.05,
        "$2 \dot \sigma$",
        fontsize=8,
        c=(0.4,) * 3,
        ha="center",
    )
    axs[0].set(xlabel="distance from peak (°)", ylabel="reliability", ylim=(-0.1, 1.2))
    axs[1].set(xticklabels=[], ylabel="reliability")


    despine(axs[0])
    despine(axs[1])

    save_figure(Path(__file__).stem)


if __name__ == "__main__":
    generate_figure()