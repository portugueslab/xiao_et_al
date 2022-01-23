from pathlib import Path

import pytest


@pytest.fixture
def behavior_scripts_dir():
    return Path(__file__).parent.parent / "behavior_analysis"


@pytest.fixture
def imaging_scripts_dir():
    return Path(__file__).parent.parent / "ot_imaging_analysis"
