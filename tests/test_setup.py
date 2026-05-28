import os
import shutil
import subprocess

import pytest

from setup import create_directories, download_and_extract_wordlists


def test_create_directories():
    create_directories()
    for directory in (
        "data/wordlists",
        "data/captures",
        "logs",
        "custom_wordlists",
        "docs/screenshots",
    ):
        assert os.path.isdir(directory)
        shutil.rmtree(directory, ignore_errors=True)


def test_download_and_extract_wordlists(monkeypatch, tmp_path):
    def mock_subprocess_run(command, *args, **kwargs):
        cmd = command if isinstance(command, list) else command.split()
        joined = " ".join(cmd)
        assert "megadl" in joined or "7z" in joined

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    download_and_extract_wordlists()
