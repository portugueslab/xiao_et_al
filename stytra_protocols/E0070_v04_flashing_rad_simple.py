from random import shuffle

import numpy as np
from stytra import Protocol
from stytra.stimulation.stimuli import FullFieldVisualStimulus
from stytra_config import ConfiguredStytra


class FlashingBarsProtocol(Protocol):
    name = "E0070_rf_estimation/v04_flashing_rad_simple"  # every protocol must have a name.

    def get_stim_sequence(self):
        n_reps = 10
        flash_dur = 4
        pause_dur = 2
        bg_col = (0,) * 3
        bar_col = (255,) * 3

        th_span = 10  # angular span of the bins

        rad = 1 / np.sqrt(2)  # radius length
        s = np.tan((th_span / 2) * np.pi / 180) * rad  # half side of the triangle
        n_triangles = 360 / th_span  # number of triangular masks

        angles = (
            np.arange(n_triangles) * th_span * np.pi / 180
        )  # angle of triangular masks

        # template triangular mask to rotate:
        polyg_points = np.array(
            [
                (0, 0),
                (s, rad),
                (-s, rad),
                (0, 0),
            ]
        )

        masks = []
        # Generate triangular masks:
        for th in angles:
            rot_mat = np.array([[np.cos(th), np.sin(th)], [-np.sin(th), np.cos(th)]])
            pts = (rot_mat.T @ polyg_points.T).T
            masks.append([(x, y) for x, y in pts + [0.5, 0.5]])

        stimuli = []
        for _ in range(n_reps):
            for mask in masks:
                stimuli.append(
                    FullFieldVisualStimulus(
                        duration=flash_dur, color=bg_col, clip_mask=list(mask)
                    )
                )
        shuffle(stimuli)

        stim_paused = []
        for stim in stimuli:
            stim_paused.extend(
                [FullFieldVisualStimulus(duration=pause_dur, color=bar_col), stim]
            )
        stim_paused.append(FullFieldVisualStimulus(duration=pause_dur, color=bar_col))
        return stim_paused


if __name__ == "__main__":
    st = ConfiguredStytra(protocol=FlashingBarsProtocol())
