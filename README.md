# Xiao et al - stimuli and behavior analysis code
Stytra stimuli and analysis scripts of Python-based analyses for the publication _Oligodendrocyte Precursor Cells Sculpt the Visual System by Regulating Axonal Remodeling_, Xiao et al, 2022. The code has ben run using `python==3.8`.
This repo is designed to make the full Python-based analysis presented in the paper fully reproducible from the data, which are shared in: TODO link to zenodo

## Description of the repo
The repo contains the following module:
 - `xiao_et_al_utils` a pip-installable module with the utility functions required by the scripts and the definition of the analysis parameters, together with the folders with the Stytra

And the following script folders:
 - `stytra_protocols`: Stytra scripts used for running the freely swimming, omr and imaging experiments
 - `behavior_analysis`: scripts for running the analysis of the freely swimming experiments and the OMR experiments.
 - `ot_imaging_analysis`: scripts for running the analysis of the imaging experiments.

## Stytra stimulation protocols
The following experiment scripts were used to run experiments with `stytra==0.8.26`:
 - `trackingfish_nostim_exp.py`: script for running the no stimulation, freely swimming larvae experiments reported in Fig.3 and Fig.S3.
 - `OMR_visual_acuity_random_grating_distance.py`: script for running the curve of contrast for the OMR response in embedded fish reported in Fig.3 and Fig.S3.
 
 ## Behavior data analysis:
 - `freely_swimming_analysis.py`: script for analyzing the no stimulation, freely swimming larvae experiments reported in Fig.3 and Fig.S3.
 - `omr_analysis.py`: script for analyzing the curve of contrast for the OMR response in embedded fish reported in Fig.3 and Fig.S3.
 
 ## Lightsheet imaging data analysis:
 Code for replicating the analysis of the functional imaging dataset can be found in the [`ot_imaging_analysis`](https://github.com/portugueslab/xiao_et_al/tree/main/ot_imaging_analysis) folder. To run the analysis:


## Instructions for reproducing the analysis
Below are the instructions to reproduce all the Python analysis of the paper.

Download data and clone repo:
1. Download the data from TODO link to zenodo
2. Uncompress locally the folder
3. Clone the `xiao_et_al` repo on your computer
4. from terminal, `cd` to the package location and install it in editable mode with `pip install -e . `
5. change the local [param_conf.ini](https://github.com/portugueslab/xiao_et_al/blob/main/ot_imaging_analysis/param_conf.ini) file argument for data location to point to the location of the downloaded data folder

Reproduce behavior analysis:
1. for the freely swimming analysis, run `> python /.../xiao_et_al/behavior_analysis/freely_swimming_analysis.py`
2. for the OMR analysis, run `> python /.../xiao_et_al/behavior_analysis/omr_analysis.py`

Reproduce imaging analysis:
1. frun in order the batch processing scripts (they can take up to several tens of minutes to run):  
    - `> python /.../xiao_et_al/ot_imaging_analysis/00_fishwise_scores.py` (extract responses for every fish), 
    - `> python /.../xiao_et_al/ot_imaging_analysis/01_pool_all_fish_data.py` (assemble pooled dataframe with data from all fish) 
    - `> python /.../xiao_et_al/ot_imaging_analysis/02_fit_rf_gauss.py` (gaussian fit)
2. At this point, running any of the figure generation scripts `fig_[x]_[name].py` will save in the figure saving location the relative panel.

