from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()
config.read(Path(__file__).parent.parent / "param_conf.ini")

############################
# Data and figures locations
DATA_MASTER_PATH = Path(config.get("main", "data_path"))

IMAGING_DATA_MASTER_PATH = DATA_MASTER_PATH / "receptive_field_imaging"
FREELY_SWIM_DATA_MASTER_PATH = DATA_MASTER_PATH / "freely_swimming"
OMR_DATA_MASTER_PATH = DATA_MASTER_PATH / "OMR"

# Folder for saved figures:
FIGURES_PATH = DATA_MASTER_PATH / "figures"
FIGURES_PATH.mkdir(exist_ok=True)

#############################################################
# Input parameters for the freely swimming behavior analysis:
ARENA_SIZE_MM = 35
ARENA_SIZE_PIXELS = 770
SMOOTH_WND_S = 0.03  # 30 ms window used to smooth data before calculating speed

#######################################
# Input parameters for the OMR analysis

# Bout detection parameters:
VIGOR_THR = 0.4  # Arbitrary vigor threshold for detection, in std units
VIGOR_WIN_SEC = 0.05  # Size of rolling window to calculate the vigor, in seconds
MIN_DURATION_S = 0.1  # Minimum bout duration, in seconds
PAD_BEFORE = 5  # Padding before bout, in pts (approx 12 ms)
PAD_AFTER = 5  # Padding after bout, in pts (approx 12 ms)

N_INIT_TRIALS_EXCLUDE = 10  # Number of initial abituation trials of the protocol
# to remove from the statistics
