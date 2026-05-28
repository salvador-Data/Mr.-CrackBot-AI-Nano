"""Hardware STL artifacts exist and are valid."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "hardware" / "generate_stl.py"

POCKET = ROOT / "hardware" / "stl" / "pocket"
LEGACY = ROOT / "hardware" / "stl"
PART_NAMES = (
    "mcb_front_shell.stl",
    "mcb_rear_shell.stl",
    "mcb_clip.stl",
)


def _ensure_stls():
    if not (POCKET / "mcb_front_shell.stl").is_file():
        subprocess.run([sys.executable, str(GEN), "--variant", "all"], check=True)


def _read_stl_tri_count(path: Path) -> int:
    data = path.read_bytes()
    assert len(data) >= 84
    return struct.unpack("<I", data[80:84])[0]


def test_pocket_stl_files_exist():
    _ensure_stls()
    for name in PART_NAMES:
        assert (POCKET / name).is_file(), name
        assert (LEGACY / name).is_file(), f"legacy {name}"


def test_cod_accessory_stls_exist():
    _ensure_stls()
    acc = ROOT / "hardware" / "stl" / "accessories"
    for name in ("cod_clip.stl", "cod_wall_dock.stl"):
        assert (acc / name).is_file(), name


def test_stl_binary_header():
    _ensure_stls()
    path = POCKET / "mcb_front_shell.stl"
    header = path.read_bytes()[:80]
    assert b"MrCrackBotAI" in header
    assert _read_stl_tri_count(path) > 10
