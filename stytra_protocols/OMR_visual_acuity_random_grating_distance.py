from random import shuffle

import numpy as np
import pandas as pd
from lightparam import Param
from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import Basic_CL_1D, GainChangerStimulus, GratingStimulus


class ClosedLoop1DProt(Protocol):
    name = "visual_acuity_omr"

    stytra_config = dict(
        tracking=dict(embedded=True, method="tail", estimator="vigor"),
        log_format="hdf5",
    )

    def __init__(self):
        super().__init__()

        self.gain = Param(-28.0, limits=(-100, 0))
        self.grating_vel = Param(10.0, unit="mm/s")
        self.inter_stim_pause = Param(10.0, unit="s", editable=False, loadable=False)
        self.grating_duration = Param(10.0, unit="s", editable=False, loadable=False)

        # Parameter controlling number of repetitions:
        self.trials_n = Param(10, editable=False, loadable=False)
        self.abituation_trials_n = Param(10, editable=False, loadable=False)
        self.baseline_grating_freq = Param(
            0.1, unit="°/mm", editable=False, loadable=False
        )
        # List of probed spatial frequencies:
        self.grating_freq_list = Param(
            [0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
            unit="°/mm",
            editable=False,
            loadable=False,
        )

    def get_stim_sequence(self):
        stimuli = [GainChangerStimulus(newgain=self.gain)]
        # # gratings
        p = self.inter_stim_pause / 2
        v = self.grating_vel
        d = self.grating_duration

        t_base = [0, p, p, p + d, p + d, 2 * p + d]
        vel_base = [0, 0, -v, -v, 0, 0]

        df = pd.DataFrame(dict(t=t_base, base_vel=vel_base))

        ClosedLoop1DGratings = type("Stim", (Basic_CL_1D, GratingStimulus), {})

        # Abituation phase:
        for _ in range(self.abituation_trials_n):
            stimuli.append(
                ClosedLoop1DGratings(
                    df_param=df,
                    grating_angle=np.pi / 2,
                    wave_shape="sine",
                    grating_period=1 / self.baseline_grating_freq,
                    grating_col_1=(255,) * 3,
                )
            )

        freq_list = self.grating_freq_list * self.trials_n
        shuffle(freq_list)

        # Actual acuity testing:
        for freq in freq_list:
            stimuli.append(
                ClosedLoop1DGratings(
                    df_param=df,
                    grating_angle=np.pi / 2,
                    wave_shape="sine",
                    grating_period=1 / freq,
                )
            )
        return stimuli


if __name__ == "__main__":
    s = Stytra(protocol=ClosedLoop1DProt())
