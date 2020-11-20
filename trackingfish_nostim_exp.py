import numpy as np
import pandas as pd
from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import Pause
from lightparam import Param

fa = 5  # repetition of stimulus


class PauseProtocol(Protocol):
    name = "free_swimming_protocol"

    stytra_config = dict(tracking=dict(method="fish"),
                         log_format="hdf5")

    def __init__(self):
        super().__init__()
        # Specify parameters as Param(something) to change them from the interface. If yuo dont care, yust type the umbers
        self.duration = Param(600., limits=(20, 3000))

    def get_stim_sequence(self):


        stimuli = [Pause(duration=self.duration)]
        return stimuli


if __name__ == "__main__":
    # We make a new instance of Stytra with this protocol as the only option:
    s = Stytra(protocol=PauseProtocol())
