"""This script calculates the analysis of swim latency and bout number for the
optomotor response experiment. It saves summary plots in the main data directory
(main_data_dir/figures/omr) and exports xls files with the data.
"""

import numpy as np
import pandas as pd
import seaborn as sns
from bouter import Experiment
from matplotlib import pyplot as plt

from xiao_et_al_utils.behavior_utils import get_exp_stats, get_summary_df
from xiao_et_al_utils.defaults import FIGURES_PATH, OMR_DATA_MASTER_PATH

sns.set(style="ticks", palette="deep")
cols = sns.color_palette()

for group in ["ntr", "cnt"]:
    print("Analysing ", group)

    master_path = OMR_DATA_MASTER_PATH / group
    paths = list(master_path.glob("*_f[0-9]"))
    exps = [Experiment(path) for path in paths]
    genotypes = [e["general"]["animal"]["comments"] for e in exps]  # animal genotypes

    # List of trial-wise bout statistics for all fish:
    trial_stats = [get_exp_stats(exp, get_spatial_period=True) for exp in exps]

    # Exclude initial 10 trials and calculate median over spatial periods for each fish:
    aggregate = [get_summary_df(s) for s in trial_stats]

    # Get summary for desired statistics from the aggregate values and save in xls file:
    for param in ["bout_n", "first_bout_latency", "swimmed_fract"]:
        summary = pd.concat(
            [aggr[param].rename(path.name) for aggr, path in zip(aggregate, paths)],
            axis=1,
        )
        summary.to_excel(str(master_path / "{}_{}_summary.xlsx".format(param, group)))

    ###############
    # Make figures:
    figure_saving_path = FIGURES_PATH / "omr" / group
    figure_saving_path.mkdir(exist_ok=True, parents=True)

    for param in ["bout_n", "first_bout_latency", "swimmed_fract"]:
        summary = pd.concat(
            [aggr[param].rename(path.name) for aggr, path in zip(aggregate, paths)],
            axis=1,
        )
        f = plt.figure(figsize=(4, 3))
        plt.plot(summary, linewidth=0.5)

        quart1 = np.percentile(summary.values, 25, axis=1)
        median = np.percentile(summary.values, 50, axis=1)
        quart2 = np.percentile(summary.values, 75, axis=1)

        plt.errorbar(
            summary.index,
            median,
            [median - quart1, quart2 - median],
            linewidth=2,
            color="k",
        )
        plt.ylabel(param)
        plt.xlabel("Spatial period (mm)")
        sns.despine()
        plt.tight_layout()
        f.savefig(str(figure_saving_path / f"{param}_{group}.pdf"), format="pdf")
