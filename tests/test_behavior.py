import subprocess
from pathlib import Path


def test_freely_swimming_analysis():
    script_dir = Path(__file__).parent.parent / "behavior_analysis"
    cmd = f"""python {str(script_dir / "freely_swimming_analysis.py")}"""
    subprocess.check_output(cmd, shell=True)


def test_omr_analysis():
    script_dir = Path(__file__).parent.parent / "behavior_analysis"
    cmd = f"""python {str(script_dir / "omr_analysis.py")}"""
    subprocess.check_output(cmd, shell=True)
