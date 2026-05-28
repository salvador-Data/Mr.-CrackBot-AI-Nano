import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest


@pytest.fixture(autouse=True)
def lab_mode(monkeypatch):
    """Default tests to simulation mode (no Wi-Fi tooling required)."""
    monkeypatch.setenv("MR_CRACKBOT_SIMULATION", "1")
    monkeypatch.setenv("MR_CRACKBOT_SKIP_INTRO", "1")
    monkeypatch.setenv("MR_CRACKBOT_USE_AI", "0")
