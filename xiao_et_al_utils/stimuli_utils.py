import numpy as np
import pandas as pd


def fix_fid(cid):
    return "_".join(cid.split("_")[:2])


def stimulus_df_from_exp0070(exp):
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

        stim_dicts.append(
            dict(t=int(log["t_start"]), pos_start=pos_start, pos_end=pos_end)
        )

    return pd.DataFrame(stim_dicts)
