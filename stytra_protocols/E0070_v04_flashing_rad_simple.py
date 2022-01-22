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
        h_mm = 7  # height of the fish in the chamber
        square_side_mm = 30  # side of the lightsheet chamber
        fish_surround_pad_r_mm = 1.5

        # Calculate number of bins to tile the radius:
        half_side = square_side_mm / 2
        max_th = np.arctan(half_side / h_mm) * 180 / np.pi
        n_bars = int(max_th / th_span)

        # Start at fish_surround_pad_r mm around the fish
        start_th = np.arctan(fish_surround_pad_r_mm / h_mm) * 180 / np.pi
        r_arr = [
            np.tan(np.pi * th / 180) * h_mm
            for th in np.arange(start_th, max_th, th_span)
        ]
        r_arr = r_arr / (np.max(r_arr) * 2)  # normalize

        # Base for circular masks:
        s = 0.05  # resolution at which to compute circle
        x = np.arange(-np.pi, np.pi + s, s)

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

        # Generate circular masks
        masks = []
        # Generate triangular masks:
        for th in angles:
            rot_mat = np.array([[np.cos(th), np.sin(th)], [-np.sin(th), np.cos(th)]])
            pts = (rot_mat.T @ polyg_points.T).T
            masks.append([(x, y) for x, y in pts + [0.5, 0.5]])

        stimuli = []
        for _ in range(n_reps):
            # Horizontal and vertical stripes:
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
        # return [VisualCombinerStimulus([DynamicLuminanceStimulus(df_param=lum_df, color=(255,) * 3, clip_mask=(0, 0, side_l, side_l)),
        #                                DynamicLuminanceStimulus(df_param=lum_df, color=(255,) * 3, clip_mask=(side_l, side_l, side_l, side_l))])]


if __name__ == "__main__":
    st = ConfiguredStytra(protocol=FlashingBarsProtocol())
