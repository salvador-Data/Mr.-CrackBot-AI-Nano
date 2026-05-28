import os
import shutil

from utils.config import check_prerequisites, ensure_directories


def test_ensure_directories():
    ensure_directories()
    for directory in ("data/wordlists", "data/captures", "temp"):
        assert os.path.isdir(directory)
    shutil.rmtree("data", ignore_errors=True)
    shutil.rmtree("temp", ignore_errors=True)


def test_check_prerequisites_simulation_mode(monkeypatch):
    monkeypatch.setenv("MR_CRACKBOT_SIMULATION", "1")
    check_prerequisites()
