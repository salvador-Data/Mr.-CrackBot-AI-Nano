from __future__ import annotations

import os
import shutil

import yaml


class Config:
    PROJECT_NAME = "Mr. CrackBot AI"
    VERSION = "1.0"

    DATA_DIR = "data"
    WORDLISTS_DIR = os.path.join(DATA_DIR, "wordlists")
    CAPTURES_DIR = os.path.join(DATA_DIR, "captures")

    DEFAULT_WORDLIST = os.path.join(WORDLISTS_DIR, "rockyou2024.txt")
    GENERATED_WORDLIST = os.path.join(WORDLISTS_DIR, "generated.txt")
    COMBINED_WORDLIST = os.path.join(WORDLISTS_DIR, "RockYou2024_combined.txt")

    NETWORK_INTERFACE = "wlan0mon"
    CAPTURE_TIMEOUT = 60

    HASHCAT_MODE = 2500
    HASHCAT_OPTIONS = "--force --opencl-device-types=1,2"

    LOG_FILE = "mr_crackbot_ai.log"
    LOG_LEVEL = "INFO"

    TEMP_DIRECTORY = "temp"
    TEMP_DIRECTORY_ENABLED = True

    ENABLE_GPU = True
    MAX_THREADS = 8

    AIRODUMP_PATH = "/usr/bin/airodump-ng"
    AIREPLAY_PATH = "/usr/bin/aireplay-ng"
    HASHCAT_PATH = "/usr/bin/hashcat"

    WORDLIST_CHUNK_SIZE = 100000
    ENABLE_SANDBOX = False
    ENFORCE_SAFE_MODE = True

    UI_THEME = "dark"
    ENABLE_ANIMATIONS = True

    SEND_EMAIL_ALERTS = False
    EMAIL_RECIPIENT = "admin@example.com"

    ENABLE_DEBUG_MODE = False
    VERBOSE_OUTPUT = True

    CUDA_PATH = "/usr/local/cuda"
    GPU_DEVICE_ID = 0
    GPU_MAX_MEMORY = 90
    GPU_FORCE_USAGE = True

    @classmethod
    def load_from_file(cls, file_path: str = "config.yaml") -> None:
        if not os.path.isfile(file_path):
            return
        with open(file_path, "r", encoding="utf-8") as file:
            config_data = yaml.safe_load(file) or {}

        for key, value in config_data.items():
            attr = key.upper()
            if hasattr(cls, attr):
                setattr(cls, attr, value)

    @classmethod
    def get_combined_wordlist_path(cls) -> str:
        return getattr(cls, "COMBINED_WORDLIST", cls.DEFAULT_WORDLIST)


def ensure_directories() -> None:
    for directory in (
        Config.WORDLISTS_DIR,
        Config.CAPTURES_DIR,
        Config.TEMP_DIRECTORY,
    ):
        os.makedirs(directory, exist_ok=True)


def check_prerequisites() -> None:
    if os.environ.get("MR_CRACKBOT_SIMULATION", "").strip() in ("1", "true", "yes"):
        return
    required_tools = ["airodump-ng", "aireplay-ng", "hashcat"]
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"Missing required tools: {', '.join(missing)}")
