import os

import pytest


@pytest.fixture(autouse=True)
def lab_mode(monkeypatch):
    """Default tests to simulation mode (no Wi-Fi tooling required)."""
    monkeypatch.setenv("MR_CRACKBOT_SIMULATION", "1")
    monkeypatch.setenv("MR_CRACKBOT_SKIP_INTRO", "1")
    monkeypatch.setenv("MR_CRACKBOT_USE_AI", "0")
