"""This script calculates the travelled distances from the freely swimming experiments,
saves a excel file with the results of each subgroup, and saves for each experiment
a pdf figure with the trajectory of that fish.
"""

import numpy as np
import pandas as pd
import seaborn as sns
from bouter import Experiment
from matplotlib import pyplot as plt
from tqdm import tqdm

from xiao_et_al_utils.defaults import (
    ARENA_SIZE_MM,
    ARENA_SIZE_PIXELS,
    FREELY_SWIM_DATA_MASTER_PATH,
    SMOOTH_WND_S,
)

sns.set(style="ticks", palette="deep")

# Numbers here are calculated from arena size in the image and in the
# physical setup:
mm_pixel = ARENA_SIZE_MM / ARENA_SIZE_PIXELS

assert len(list(FREELY_SWIM_DATA_MASTER_PATH.glob("*"))) > 0
# Loop over all groups subdirectories:
for master_path in FREELY_SWIM_DATA_MASTER_PATH.glob("*"):
    # Find list with all fish directories:
    fish_paths = list(master_path.glob("*f[0-9]"))

    print("Folders: \n" + "\n".join([str(f) for f in fish_paths]))

    distances_travelled = []

    assert len(list(master_path.glob("*f[0-9]"))) > 0
    for fish_path in tqdm(list(master_path.glob("*f[0-9]"))):
        beh_df = Experiment(fish_path).behavior_log
        beh_df = beh_df.set_index(["t"])  # set time as index

        dt = np.median(np.diff(beh_df.index))  # find timepoint duration in sec

        # Smooth the velocities:
        smooth_df = beh_df.rolling(int(SMOOTH_WND_S / dt), center=True).mean()

        # Calculate speed:
        speed = np.sqrt(smooth_df["f0_vx"] ** 2 + smooth_df["f0_vy"] ** 2)

        # Get distance integrating speed, accounting for calibration:
        distances_travelled.append(np.sum(speed) * mm_pixel)

        # plot the trajectory:
        f, ax = plt.subplots(figsize=(5, 5))

        bar_length_mm = 10  # size of the bar length

        ax.plot(beh_df["f0_x"] * mm_pixel, beh_df["f0_y"] * mm_pixel)
        ax.axis("equal")

        # a bunch of ugly stuff for the bar:
        ax.set_yticks([])
        ax.set_xticks([0, bar_length_mm])
        ax.set_xticklabels([])
        ax.set_xticks([bar_length_mm / 2], minor=True)
        ax.set_xticklabels(["{} mm".format(bar_length_mm)], minor=True)
        ax.tick_params(length=0, which="both")
        ax.set_title(fish_path.name)

        sns.despine(left=True, trim=True)
        f.savefig(str(fish_path / "trajectory_plot.pdf"), format="pdf")

    # Create and save DataFrame to excel:
    pd.DataFrame(
        np.array(distances_travelled),
        columns=["distance (mm)"],
        index=[f.name for f in fish_paths],
    ).to_excel(master_path / "all_distances.xlsx")
