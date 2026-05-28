from __future__ import annotations

import csv
import os
import subprocess
from pathlib import Path


def _simulation_enabled() -> bool:
    return os.environ.get("MR_CRACKBOT_SIMULATION", "").strip() in ("1", "true", "yes")


def _sample_networks() -> list[dict[str, str]]:
    return [
        {"bssid": "AA:BB:CC:DD:EE:01", "ssid": "Lab_Network", "channel": "6"},
        {"bssid": "AA:BB:CC:DD:EE:02", "ssid": "Guest_WiFi", "channel": "11"},
    ]


def scan_networks(interface: str = "wlan0mon") -> list[dict[str, str]]:
    if _simulation_enabled():
        return _sample_networks()

    output_prefix = Path("data/captures/scan_results")
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "airodump-ng",
        "--write",
        str(output_prefix),
        "--output-format",
        "csv",
        interface,
    ]
    subprocess.run(command, check=False, timeout=30)

    csv_path = Path(f"{output_prefix}-01.csv")
    if not csv_path.is_file():
        return _sample_networks()
    return parse_scan_results(csv_path)


def parse_scan_results(file_path: str | Path) -> list[dict[str, str]]:
    networks: list[dict[str, str]] = []
    path = Path(file_path)
    if not path.is_file():
        return networks

    with path.open("r", encoding="utf-8", errors="ignore") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or row[0].strip().startswith("BSSID"):
                continue
            if len(row) > 13 and row[0].strip():
                networks.append(
                    {
                        "bssid": row[0].strip(),
                        "channel": row[3].strip(),
                        "ssid": row[13].strip() or "<hidden>",
                    }
                )
    return networks
