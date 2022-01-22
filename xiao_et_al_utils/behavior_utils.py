import pandas as pd
import numpy as np
from numba import njit
from xiao_et_al_utils.defaults import VIGOR_THR, VIGOR_WIN_SEC, MIN_DURATION_S, \
    PAD_BEFORE, PAD_AFTER, N_INIT_TRIALS_EXCLUDE


@njit
def extract_segments_above_thresh(
        vel, threshold=0.1, min_duration=20, pad_before=12, pad_after=25
):
    """ Extract bouts from velocity or vigor, numba-ized for speed.
    This function exists also in bouter, but was used from a local version for the
    paper analysis and so is duplicated for consistency.

    :param vel:  velocity or vigor array to threshold.
    :param threshold: threshold for detection.
    :param min_duration: minimum duration for a bout to be included.
    :param pad_before: n of points for pre-start padding in the cropped segment.
    :param pad_after: n of points for post-end padding in the cropped segment.
    :return: tuple containing the list of cropped bouts, and a list specifying if
    each bout was contiguous or had interruptions of nans in the middle.
    """
    bouts = []
    in_bout = False
    start = 0
    connected = []
    continuity = False
    i = pad_before + 1
    bout_ended = pad_before

    # Loop on the trace and check for contiguous threshold crossing:
    while i < vel.shape[0] - pad_after:
        if np.isnan(vel[i]):
            continuity = False
            if in_bout:
                in_bout = False

        elif i > bout_ended and vel[i - 1] < threshold < vel[i] and not in_bout:
            in_bout = True
            start = i - pad_before

        elif vel[i - 1] > threshold > vel[i] and in_bout:
            in_bout = False
            if i - start > min_duration:
                bouts.append((start, i + pad_after))
                bout_ended = i + pad_after
                if continuity:
                    connected.append(True)
                else:
                    connected.append(False)
            continuity = True

        i += 1

    return bouts, connected

def get_exp_stats(exp, get_spatial_period=False):
    """ Useful for extracing bouts from velocity or vigor, numba-ized for speed.

    :param exp:  a Stytra Experiment object.
    :param get_spatial_period: if True, spatial period is read from the log and included in the df.
    :return: pandas DataFrame with trial-wise experiment statistics
    """
    
    tail_log_df = exp.behavior_log.set_index("t")  # DataFrame with the tail trace
    stim_log_df = exp.stimulus_log.set_index("t")  # DataFrame with the stimulus
    
    # Calculate average tracking framerate to calculate the window:
    tail_dt = np.diff(tail_log_df.index).mean()
    
    # Calculate vigor from tail trace:
    vigor = tail_log_df["tail_sum"].rolling(int(VIGOR_WIN_SEC/tail_dt), center=True).std().values
    
    # Extract bouts:
    bouts_idxs, _ = extract_segments_above_thresh(vigor, VIGOR_THR, min_duration=int(MIN_DURATION_S/tail_dt),
                                             pad_before=PAD_BEFORE, pad_after=PAD_AFTER)

    # Calculate bouts start and end times:
    bout_starts = np.array([tail_log_df["tail_sum"].index[b[0]] for b in bouts_idxs])
    bout_ends = np.array([tail_log_df["tail_sum"].index[b[1]] for b in bouts_idxs])

    
    # Use derivative to find trial start and trial end from stimulus velocity:
    trial_s = stim_log_df.index[np.ediff1d(stim_log_df["general_cl1D_base_vel"], to_begin=0) < 0]
    trial_e = stim_log_df.index[np.ediff1d(stim_log_df["general_cl1D_base_vel"], to_begin=0) > 0]

    # Initialize dataframe with trial-wise swimming statistics:
    trial_df = pd.DataFrame(dict(start=trial_s, 
                                 end=trial_e, 
                                 inter_bout_t=np.nan, 
                                 bout_n=np.nan, 
                                 bout_duration=np.nan,
                                 first_bout_latency=trial_e-trial_s  # Default latency is stim duration
                                 ), 
                            index=np.arange(len(trial_s)))
    
    # Loop over trials, and fill dataframe with bout statistics:
    for i in range(len(trial_df)):
        
        # Find bouts in temporal boundaries of trial i:
        bout_idxs = np.argwhere((bout_starts > trial_df.loc[i, "start"]) 
                                & (bout_ends < trial_df.loc[i, "end"]))[:,0]
        trial_df.loc[i, "bout_n"] = len(bout_idxs)
        
        # If there are bouts in the trial:
        if len(bout_idxs) > 0:
            trial_df.loc[i, "first_bout_latency"] = bout_starts[bout_idxs[0]] - trial_df.loc[i, "start"]
            trial_df.loc[i, "bout_duration"] = (bout_ends[bout_idxs] - bout_starts[bout_idxs]).mean()

            # If we have at least 2 bouts we calculate inter-bout:
            if len(bout_idxs) > 1:
                trial_df.loc[i, "inter_bout_t"] = (bout_starts[bout_idxs[1:]] - bout_ends[bout_idxs[:-1]]).mean()
    
    if get_spatial_period:
        # Spatial periods of each trial, it it was a grating trial:    
        trial_df["spatial_period"] = [s["grating_period"] for s in exp["stimulus"]["log"] 
                                      if "grating_period" in s.keys()]
                
    return trial_df


def get_summary_df(trial_stats_table):
    trial_stats_table = trial_stats_table.copy()

    # Calculate median of computed statistics after excluding abituating trials
    table = trial_stats_table[N_INIT_TRIALS_EXCLUDE:].groupby("spatial_period").median()

    # Calculate fraction of trials with at least one bout
    trial_stats_table["swimmed_fract"] = (
                trial_stats_table["bout_n"] > 0).values.astype(np.float)
    table["swimmed_fract"] = \
    trial_stats_table[N_INIT_TRIALS_EXCLUDE:].groupby("spatial_period").mean()[
        "swimmed_fract"]
    return table



