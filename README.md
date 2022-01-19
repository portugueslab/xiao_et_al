# Xiao et al - stimuli and behavior analysis code
Stytra stimuli and analysis notebooks for the publication _Oligodendrocyte Precursor Cells Sculpt the Visual System by Regulating Axonal Remodeling_, Xiao et al, 2022. The code has ben run using `python==3.7`

## Stytra stimulation protocols
The following experiment scripts were used to run experiments with `stytra==0.8.26`:
 - `trackingfish_nostim_exp.py`: script for running the no stimulation, freely swimming larvae experiments reported in Fig.3 and Fig.S3.
 - `trackingfish_nostim_exp.py`: script for running the curve of contrast for the OMR response in embedded fish reported in Fig.3 and Fig.S3.
 
 ## Behavior data analysis:
 - `Freely swimming analysis.ipynb`: Jupyter Notebook for analyzing the no stimulation, freely swimming larvae experiments reported in Fig.3 and Fig.S3.
 - `OMR - visual acuity random gratings.ipynb`: Jupyter Notebook for analyzing the curve of contrast for the OMR response in embedded fish reported in Fig.3 and Fig.S3.
 
 ## Lightsheet imaging data analysis:
 Code for replicating the analysis of the functional imaging dataset can be found in the [`ot_imaging_analysis`](https://github.com/portugueslab/xiao_et_al/tree/main/ot_imaging_analysis) folder. To run the analysis:
 1. clone the package on your computer
 2. from terminal, `cd` to the package location and install it in editable mode with `pip install -e . `
 3. change the [param_conf.ini](https://github.com/portugueslab/xiao_et_al/blob/main/ot_imaging_analysis/param_conf.ini) file argument for data location to point to the downloaded data folder, and the figure saving location to a path of choice
 4. run in order the batch processing scripts `00_fishwise_scores.py` (extract responses for every fish), `01_pool_all_fish_data.py` (assemble pooled dataframe with data from all fish) and `02_fit_rf_gauss.py` (gaussian fit)
 5. at this point, running any of the figure generation scripts `fig_[x]_[name].py` will save in the figure saving location the relative panel.

