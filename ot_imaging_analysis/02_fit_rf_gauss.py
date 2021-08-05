import numpy as np
import flammkuchen as fl
from tqdm import tqdm
from pathlib import Path
from configparser import ConfigParser

from scipy.optimize import curve_fit

config = ConfigParser()
config.read('param_conf.ini')

MASTER_PATH = Path(config.get("main", "data_path"))
REL_SCORE_THR = config.getfloat('main', 'rel_score_thr')
N_STIMS = 36


def _gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))


# Get matrix with centered responses for all cells:
all_cells_df = fl.load(MASTER_PATH / "pooled_dfs.h5", "/all_cells_df")
full_data_mat = all_cells_df.loc[:, [f"rel_reord_{i}" for i in range(N_STIMS)]].values
n_cells = full_data_mat.shape[0]

popt = np.full((n_cells, 3), np.nan)
pcov = np.full((n_cells, 3, 3), np.nan)
x = np.arange(N_STIMS)

# Loop and fit individual cells:
for i in tqdm(range(n_cells)):
    try:
        y = full_data_mat[i, :]
        mean = sum(x * y) / sum(y)  # guess mean as center of mass
        sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))  # guess variance as variance
        # Fit gaussian:
        popt[i, :], pcov[i, :, :] = curve_fit(_gaussian, x, y, p0=[max(y), mean, sigma])

    except RuntimeError:
        pass

fl.save(MASTER_PATH / "gaussian_fit.h5", dict(popt=popt,
                                              pcov=pcov))
