import subprocess
from pathlib import Path


def test_imaging_analysis():
    script_dir = Path(__file__).parent.parent / "ot_imaging_analysis"
    cmd = f"""python {str(script_dir / "00_fishwise_scores.py")}
              python {str(script_dir / "01_pool_all_fish_data.py")}
              python {str(script_dir / "02_fit_rf_gauss.py")}
              python {str(script_dir / "fig_3i_overview.py")}
              python {str(script_dir / "fig_3j_example_traces.py")}
              python {str(script_dir / "fig_3kl_s7abef_histograms.py")}
              python {str(script_dir / "fig_s7c_retinotopy.py")}
              python {str(script_dir / "fig_s7d_rf_estim.py")}"""
    subprocess.check_output(cmd, shell=True)
