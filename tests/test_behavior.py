"""Test behavior analysis scripts.
"""


def test_freely_swimming_analysis_script(behavior_scripts_dir, script_runner):
    ret = script_runner.run(
        f"{str(behavior_scripts_dir / 'freely_swimming_analysis.py')}"
    )
    assert ret.success


def test_omr_analysis_script(behavior_scripts_dir, script_runner):
    ret = script_runner.run(f"{str(behavior_scripts_dir / 'omr_analysis.py')}")
    assert ret.success
    assert ret.stderr == ""
