from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()
config.read(Path(__file__).parent.parent / 'param_conf.ini')

DATA_MASTER_PATH = Path(config.get('main', 'data_path'))

IMAGING_DATA_MASTER_PATH = DATA_MASTER_PATH / "receptive_field_imaging"
FREELY_SWIM_DATA_MASTER_PATH = DATA_MASTER_PATH / "freely_swimming"
OMR_DATA_MASTER_PATH = DATA_MASTER_PATH / "OMR"

# Folder for saved figures:
FIGURES_PATH = DATA_MASTER_PATH / "figures"
FIGURES_PATH.mkdir(exist_ok=True)

# Input parameters for the freely swimming behavior analysis:
ARENA_SIZE_MM = 35
ARENA_SIZE_PIXELS = 770
SMOOTH_WND_S = 0.03  # 30 ms window used to smooth data before calculating speed
