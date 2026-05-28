#!/usr/bin/env python3
"""
Generate Mr. CrackBot AI Nano enclosure and accessory STL files.

Variants:
  pocket — CYD 2.8" + Jetson Nano stack (default, also copied to hardware/stl/)
  all    — pocket shells + COD clip + wall dock

Usage:
  python hardware/generate_stl.py
  python hardware/generate_stl.py --variant all
"""

from __future__ import annotations

import argparse
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parent
LEGACY_OUT = ROOT / "stl"
ACCESSORIES = ROOT / "stl" / "accessories"

# Pocket enclosure — CYD 2432S028 + Jetson Nano 4GB carrier
W, H, D = 102.0, 78.0, 30.0
WALL = 2.0
USBC_W, USBC_H = 12.0, 6.0
DISPLAY_W, DISPLAY_H, DISPLAY_Z = 68.0, 50.0, 14.0
STANDOFFS = [(14, 38), (58, 38), (14, 58), (58, 58)]


@dataclass
class Tri:
    n: tuple[float, float, float]
    v1: tuple[float, float, float]
    v2: tuple[float, float, float]
    v3: tuple[float, float, float]


def _cross(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    ln = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
    return (nx / ln, ny / ln, nz / ln)


def _box_tris(x: float, y: float, z: float, w: float, h: float, d: float) -> list[Tri]:
    p = [
        (x, y, z), (x + w, y, z), (x + w, y + h, z), (x, y + h, z),
        (x, y, z + d), (x + w, y, z + d), (x + w, y + h, z + d), (x, y + h, z + d),
    ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    tris: list[Tri] = []
    for a, b, c, d in faces:
        tris.append(Tri(_cross(p[a], p[b], p[c]), p[a], p[b], p[c]))
        tris.append(Tri(_cross(p[a], p[c], p[d]), p[a], p[c], p[d]))
    return tris


def _cylinder_tris(cx: float, cy: float, z0: float, z1: float, r: float, seg: int = 16) -> list[Tri]:
    import math

    tris: list[Tri] = []
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        b0, p0, p1 = (cx, cy, z0), (x0, y0, z0), (x1, y1, z0)
        q0, q1 = (x0, y0, z1), (x1, y1, z1)
        tris.append(Tri(_cross(b0, p0, p1), b0, p0, p1))
        tris.append(Tri(_cross(q0, q1, p1), q0, q1, p1))
        tris.append(Tri(_cross(p0, q0, p1), p0, q0, p1))
        tris.append(Tri(_cross(p1, q0, q1), p1, q0, q1))
    return tris


def write_binary_stl(path: Path, tris: Iterable[Tri]) -> None:
    tri_list = list(tris)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = b"MrCrackBotAI enclosure STL"
    header = header + bytes(80 - len(header))
    with path.open("wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(tri_list)))
        for t in tri_list:
            f.write(struct.pack("<3f", *t.n))
            f.write(struct.pack("<3f", *t.v1))
            f.write(struct.pack("<3f", *t.v2))
            f.write(struct.pack("<3f", *t.v3))
            f.write(struct.pack("<H", 0))


def mesh_front_shell() -> list[Tri]:
    tris: list[Tri] = []
    tris += _box_tris(0, 0, 0, W, D / 2, WALL)
    tris += _box_tris(0, D / 2, 0, W, D / 2, WALL)
    tris += _box_tris(0, 0, 0, WALL, D, H)
    tris += _box_tris(W - WALL, 0, 0, WALL, D, H)
    tris += _box_tris(0, 0, H - WALL, W, D, WALL)
    tris += _box_tris(0, 0, 0, W, WALL, H)
    x0 = (W - DISPLAY_W) / 2
    yf = D - WALL
    tris += _box_tris(0, yf, DISPLAY_Z + DISPLAY_H, W, WALL, H - (DISPLAY_Z + DISPLAY_H))
    tris += _box_tris(0, yf, 0, W, WALL, DISPLAY_Z)
    tris += _box_tris(0, yf, DISPLAY_Z, x0, WALL, DISPLAY_H)
    tris += _box_tris(x0 + DISPLAY_W, yf, DISPLAY_Z, W - (x0 + DISPLAY_W), WALL, DISPLAY_H)
    tris += _box_tris(W / 2 - USBC_W / 2, yf, 2, USBC_W, WALL + 0.5, USBC_H)
    for sx, sz in STANDOFFS:
        tris += _cylinder_tris(sx, D / 2 + 2, sz, sz + 5, 2.0)
    return tris


def mesh_rear_shell() -> list[Tri]:
    tris: list[Tri] = []
    tris += _box_tris(0, 0, 0, W, D / 2, WALL)
    tris += _box_tris(0, 0, 0, WALL, D / 2, H)
    tris += _box_tris(W - WALL, 0, 0, WALL, D / 2, H)
    tris += _box_tris(0, 0, H - WALL, W, D / 2, WALL)
    tris += _box_tris(0, D / 2 - WALL, 0, W, WALL, H)
    tris += _box_tris(0, 0, 0, W, WALL, H)
    tris += _box_tris(WALL + 2, WALL, WALL + 2, W - 2 * WALL - 4, 3, 22)
    for i in range(3):
        tris += _box_tris(W / 2 - 8, 0, H / 2 - 10 + i * 7, 16, WALL + 1, 3)
    for gx in (26, W - 26):
        tris += _cylinder_tris(gx, -1, H / 2 - 10, H / 2 + 10, 3.5, seg=18)
    tris += _box_tris(W / 2 - USBC_W / 2, -0.5, 2, USBC_W, WALL + 1, USBC_H)
    tris += _box_tris(20, -0.3, 10, 62, 0.8, 4)
    tris += _box_tris(28, -0.3, 5, 46, 0.6, 3)
    return tris


def mesh_clip() -> list[Tri]:
    tris: list[Tri] = []
    bar_w, arm_w, arm_h, dep = 56, 8, 14, 5
    x0 = (W - bar_w) / 2
    tris += _box_tris(x0, 0, arm_h - 2, bar_w, dep, 4)
    for ax in (x0 - arm_w + 2, x0 + bar_w - 2):
        tris += _box_tris(ax, 0, 0, arm_w, dep, arm_h)
        tris += _box_tris(ax + 1, dep - 1, arm_h - 4, arm_w - 2, 2, 4)
    return tris


def mesh_cod_clip() -> list[Tri]:
    """Belt / pocket clip accessory (COD STL pack)."""
    tris: list[Tri] = []
    tris += _box_tris(0, 0, 0, 18, 6, 28)
    tris += _box_tris(2, 6, 4, 14, 10, 20)
    tris += _box_tris(4, 16, 8, 10, 3, 12)
    tris += _cylinder_tris(9, 3, 0, 6, 4, seg=14)
    return tris


def mesh_wall_dock() -> list[Tri]:
    """Wall dock — cradle for pocket enclosure."""
    tris: list[Tri] = []
    tris += _box_tris(0, 0, 0, W + 8, 12, 8)
    tris += _box_tris(4, 12, 2, W, 6, H - 4)
    tris += _box_tris(4, 18, 2, 6, 4, H - 4)
    tris += _box_tris(W - 2, 18, 2, 6, 4, H - 4)
    tris += _box_tris(W / 2 - 14, 22, H / 2 - 6, 28, 8, 12)
    return tris


def export_pocket(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    builders: dict[str, Callable[[], list[Tri]]] = {
        "mcb_front_shell.stl": mesh_front_shell,
        "mcb_rear_shell.stl": mesh_rear_shell,
        "mcb_clip.stl": mesh_clip,
    }
    for name, fn in builders.items():
        path = out_dir / name
        tris = fn()
        write_binary_stl(path, tris)
        print(f"Pocket: {path} ({len(tris)} tris)")


def export_accessories(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in (
        ("cod_clip.stl", mesh_cod_clip),
        ("cod_wall_dock.stl", mesh_wall_dock),
    ):
        path = out_dir / name
        tris = fn()
        write_binary_stl(path, tris)
        print(f"Accessory: {path} ({len(tris)} tris)")


def generate_pocket() -> None:
    out_dir = ROOT / "stl" / "pocket"
    export_pocket(out_dir)
    LEGACY_OUT.mkdir(parents=True, exist_ok=True)
    for stl in out_dir.glob("mcb_*.stl"):
        shutil.copy2(stl, LEGACY_OUT / stl.name)
        print(f"Legacy copy: {LEGACY_OUT / stl.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CrackBot enclosure STLs")
    parser.add_argument("--variant", choices=("pocket", "all"), default="pocket")
    args = parser.parse_args()
    print("Mr. CrackBot AI Nano — STL export")
    generate_pocket()
    if args.variant == "all":
        export_accessories(ACCESSORIES)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
