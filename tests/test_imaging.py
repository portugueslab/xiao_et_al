"""Test behavior analysis scripts.
"""


def test_imaging_analysis(imaging_scripts_dir, script_runner):
    for script_name in [
        "00_fishwise_scores.py",
        "01_pool_all_fish_data.py",
        "02_fit_rf_gauss.py",
        "fig_3i_overview.py",
        "fig_3j_example_traces.py",
        "fig_3kl_s7abef_histograms.py",
        "fig_s7c_retinotopy.py",
        "fig_s7d_rf_estim.py",
    ]:
        ret = script_runner.run(f"{str(imaging_scripts_dir / script_name)}")
        assert ret.success
