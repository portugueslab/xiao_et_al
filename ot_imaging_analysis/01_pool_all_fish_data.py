"""This script put together in teo pandas DataFrames a registry of all experiments
 (exp_df) and the reliability scores and tuning curves from all cells from all
 experiments """

import pandas as pd
import flammkuchen as fl
from tqdm import tqdm
from pathlib import Path
from configparser import ConfigParser

config = ConfigParser()
config.read('param_conf.ini')

MASTER_PATH = Path(config.get('main', 'data_path'))
REL_SCORE_THR = config.getfloat('main', 'rel_score_thr')

# Loop over all experiments, concatenate cells dfs and collect cumulative infos:
cell_dfs = []
exp_dfs = []
for df_path in tqdm(MASTER_PATH.glob("*/cell_df.h5")):
    cell_df = fl.load(df_path)

    # Compute mean amplitude of response for cells in the tectum:
    mn_amplitude = cell_df.loc[cell_df["in_tectum"], "max_amp"].mean()

    exp_dfs.append(dict(fid=cell_df.loc[0, "fid"],
                        gen=cell_df.loc[0, "gen"],
                        gen_long=cell_df.loc[0, "gen_long"],
                        n_cells=len(cell_df),
                        above_rel_thr=sum(cell_df["in_tectum"] & (cell_df["max_rel"] > REL_SCORE_THR)),
                        mn_amplitude=mn_amplitude))
    cell_dfs.append(cell_df)

# Concatenate to generate pooled dataframes:
all_cells_df = pd.concat(cell_dfs, axis=0)
all_cells_df = all_cells_df.set_index(all_cells_df["cid"])

exp_df = pd.DataFrame(exp_dfs)
exp_df = exp_df.set_index("fid")

fl.save(MASTER_PATH / "pooled_dfs.h5", dict(exp_df=exp_df,
                                            all_cells_df=all_cells_df))
