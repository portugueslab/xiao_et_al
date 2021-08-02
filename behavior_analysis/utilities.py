import json
from pathlib import Path
import pandas as pd
import numpy as np
from numba import jit


class Experiment(dict):
    """Utility class to load stytra files, across versions. It simply provide an API
    to access easily data and metadata from a behavioral experiment. There might be some redundant
    code for loading across different Stytra versions formats.

    Parameters
    ----------
    path :


    Returns
    -------

    """

    log_mapping = dict(
        stimulus_param_log=["dynamic_log", "stimulus_log", "stimulus_param_log"],
        estimator_log=["estimator_log"],
        behavior_log=["tracking_log", "log", "behavior_log"],
    )

    def __init__(self, path, session_id=None):
        # Prepare path:
        inpath = Path(path)

        if inpath.suffix == ".json":
            self.path = inpath.parent
            session_id = inpath.name.split("_")[0]

        else:
            self.path = Path(path)

            if session_id is None:
                meta_files = list(self.path.glob("*metadata.json"))

                # Load metadata:
                if len(meta_files) == 0:
                    raise FileNotFoundError("No metadata file in specified path!")
                elif len(meta_files) > 1:
                    raise FileNotFoundError(
                        "Multiple metadata files in specified path!"
                    )
                else:
                    session_id = str(meta_files[0].name).split("_")[0]

        self.session_id = session_id
        metadata_file = self.path / (session_id + "_metadata.json")

        source_metadata = json.load(open(metadata_file))

        # Temporary workaround:
        try:
            source_metadata["behavior"] = source_metadata.pop("tracking")
        except KeyError:
            pass

        super().__init__(**source_metadata)

        self._stimulus_param_log = None
        self._behavior_log = None
        self._estimator_log = None

    def _get_log(self, log_name):
        uname = "_" + log_name

        if getattr(self, uname) is None:
            for possible_name in self.log_mapping[log_name]:
                try:
                    logname = next(
                        self.path.glob(self.session_id + "_" + possible_name + ".*")
                    ).name
                    setattr(self, uname, self._load_log(logname))
                    break
                except StopIteration:
                    pass
            else:
                raise ValueError(log_name + " does not exist")

        return getattr(self, uname)

    @property
    def stimulus_param_log(self):
        return self._get_log("stimulus_param_log")

    @property
    def behavior_log(self):
        return self._get_log("behavior_log")

    def _load_log(self, data_name):
        """

        Parameters
        ----------
        data_name :


        Returns
        -------

        """

        file = self.path / data_name
        if file.suffix == ".csv":
            return pd.read_csv(str(file), delimiter=";").drop("Unnamed: 0", axis=1)
        elif file.suffix == ".h5" or file.suffix == ".hdf5":
            return pd.read_hdf(file)
        else:
            raise ValueError(
                str(data_name) + " format is not supported, trying to load " + str(file)
            )

    
#--------------------------------------Bout extraction--------------------------------------#


@jit(nopython=True)
def extract_segments_above_thresh(
    vel, threshold=0.1, min_duration=20, pad_before=12, pad_after=25
):
    """ Extract bouts from velocity or vigor, numba-ized for speed.

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


#--------------------------------------Bout statistics--------------------------------------#

def get_exp_stats(exp, get_spatial_period=False):
    """ Useful for extracing bouts from velocity or vigor, numba-ized for speed.

    :param exp:  a Stytra Experiment object.
    :param get_spatial_period: if True, spatial period is read from the log and included in the df.
    :return: pandas DataFrame with trial-wise experiment statistics
    """
    VIGOR_THR = 0.4  # Arbitrary vigor threshold for detection, in std units
    VIGOR_WIN_SEC = 0.5  # Size of rolling window to calculate the vigor, in seconds
    MIN_DURATION_S = 0.1  # Minimum bout duration, in seconds
    PAD_BEFORE = 5  # Padding before bout, in pts
    PAD_AFTER = 5  # Padding after bout, in pts
    
    tail_log_df = exp.behavior_log.set_index("t")  # DataFrame with the tail trace
    stim_log_df = exp.stimulus_param_log.set_index("t")  # DataFrame with the stimulus
    
    # Calculate average tracking framerate to calculate the window:
    tail_dt = np.diff(tail_log_df.index).mean()
    
    # Calculate vigor from tail trace:
    vigor = tail_log_df["tail_sum"].rolling(int(VIGOR_WIN_SEC/tail_dt), center=True).std().values
    
    # Extract bouts:
    bouts_idxs, _ = extract_segments_above_thresh(vigor, VIGOR_THR, min_duration=int(MIN_DURATION_S/tail_dt), 
                                             pad_before=PAD_BEFORE, pad_after=PAD_AFTER, skip_nan=True)
    
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



