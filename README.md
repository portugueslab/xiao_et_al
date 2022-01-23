![example workflow](https://github.com/portugueslab/xiao_et_al/actions/workflows/main.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/portugueslab/xiao_et_al/badge.svg)](https://coveralls.io/github/portugueslab/xiao_et_al)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![code style](https://img.shields.io/badge/code%20style-black-black)


# Oligodendrocyte Precursor Cells Sculpt the Visual System by Regulating Axonal Remodeling [protocols and analysis code]
Stytra stimuli and analysis scripts of Python-based analyses for the publication _Oligodendrocyte Precursor Cells Sculpt the Visual System by Regulating Axonal Remodeling_, Xiao et al, 2022. The code has ben run using `python==3.8`.
This repo is designed to make the full Python-based analysis presented in the paper fully reproducible. Automatic testing and sample data are provided to ensure the workflow can run. The complete dataset for replicating all the paper plots(~9 GB) can be found [here](https://zenodo.org/record/5894604#.Ye1AuS8w1QI). 

## Description of the repo
The repo contains the following module:
 - `xiao_et_al_utils` a pip-installable module with the utility functions required by the scripts and the definition of the analysis parameters, together with the folders with the Stytra

And the following script folders:
 - `stytra_protocols`: Stytra scripts used for running the freely swimming, omr and imaging experiments
 - `behavior_analysis`: scripts for running the analysis of the freely swimming experiments and the OMR experiments
 - `ot_imaging_analysis`: scripts for running the analysis of the imaging experiments

#### Stytra stimulation protocols:
The following experiment scripts were used to run experiments with `stytra==0.8.26`:
 - `trackingfish_nostim_exp.py`: script for running the no stimulation, freely swimming larvae experiments reported in Fig.S6
 - `OMR_visual_acuity_random_grating_distance.py`: script for running the curve of contrast for the OMR response in embedded fish reported in Fig.3 and Fig.S6
 - `E0070_v04_flashing_rad_simple.py`: script used for running under the lightsheet microscope the receptive field estimation experiments reported in Fig.3
 
 #### Behavior data analysis:
 - `freely_swimming_analysis.py`: script for analyzing the no stimulation, freely swimming larvae experiments reported in Fig.S6
 - `omr_analysis.py`: script for analyzing the curve of contrast for the OMR response in embedded fish reported in Fig.3 and Fig.S6
 
 #### Lightsheet imaging data analysis:
 Code for replicating the analysis of the functional imaging dataset can be found in the [`ot_imaging_analysis`](https://github.com/portugueslab/xiao_et_al/tree/main/ot_imaging_analysis) folder.
- the numbered files `00_fishwise_scores.py`, `01_pool_all_fish_data.py`, `02_fit_rf_gauss.py` contain the preprocessing scripts that compute cell responses strengths, aggregate data, and do the receptive field fit
- the `fig_[n]_[description].py` files contain the code that generate each of the panels of the paper that pertain to the imaging experiments.

There is an additional file, `run_suite2p.py`, that was used to align the imaging, segment the ROI and extract their fluorescence traces using `suite2p==0.7.2`. Since the raw imaging data is too big to be shared, only the results of this script are shared to reproduce the paper figures, and the script is kept here only to log the parameters used with the `suite2p` algorithm.


## Instructions for reproducing the analysis
Below are the instructions to reproduce all the Python analysis of the paper.

Download data and clone repo:
1. Download the data from [here](https://zenodo.org/record/5894604#.Ye1AuS8w1QI)
2. Uncompress locally the folder
3. From the terminal, clone the `xiao_et_al` repo on your computer:
    ```bash
    > git clone https://github.com/portugueslab/xiao_et_al
    ```
5. `cd` to the package location:
    ```bash
    > cd xiao_et_al
    ```
6. [Optional] Create a new environment to run the script:
    ```bash
    > conda create -n xiaotest python==3.8
    > conda activate xiaotest
    ```
7. and install it in editable mode:
    ```bash
    > pip install -e . 
    ```
7. Find you local param_conf.ini file in the repo, and change it to set the argument for data location to point to the location of the downloaded data folder

#### Reproduce behavior analysis:
1. for the freely swimming analysis, run `> python /.../xiao_et_al/behavior_analysis/freely_swimming_analysis.py`
2. for the OMR analysis, run `> python /.../xiao_et_al/behavior_analysis/omr_analysis.py`

#### Reproduce imaging analysis:
1. frun in order the batch processing scripts (they can take up to several tens of minutes to run):  
    - `> python /.../xiao_et_al/ot_imaging_analysis/00_fishwise_scores.py` (extract responses for every fish), 
    - `> python /.../xiao_et_al/ot_imaging_analysis/01_pool_all_fish_data.py` (assemble pooled dataframe with data from all fish) 
    - `> python /.../xiao_et_al/ot_imaging_analysis/02_fit_rf_gauss.py` (gaussian fit)
2. At this point, running any of the figure generation scripts `fig_[figN]_[descritpion].py` will save in the figure saving location the panel `figN` from the paper.

#### Reproduce entire analysis through tests:
The paper figures can also be all generated in the data folder running `pytest` in the repo after having installed the `[dev]` dependencies:
```bash
> pip install -e .[dev]
> pytest
```


