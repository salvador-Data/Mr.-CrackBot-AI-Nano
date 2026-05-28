# Hardware — 3D printed enclosure

Mr. CrackBot AI Nano ships as a **pocket lab appliance** for authorized Wi‑Fi research: CYD (Cheap Yellow Display) 2.8" touchscreen + Jetson Nano 4GB in a snap-fit shell, with optional belt clip and wall dock STLs.

## Quick start

```bash
# Pocket enclosure (3 parts)
python hardware/generate_stl.py

# Pocket + COD accessories (clip + wall dock)
python hardware/generate_stl.py --variant all
```

## STL locations

| Set | Directory | Parts |
|-----|-----------|-------|
| **Pocket** | `hardware/stl/pocket/` | `mcb_front_shell.stl`, `mcb_rear_shell.stl`, `mcb_clip.stl` |
| Legacy | `hardware/stl/` | Same as pocket (auto-copied) |
| **COD pack** | `hardware/stl/accessories/` | `cod_clip.stl`, `cod_wall_dock.stl` |

### Fit targets

| Component | Notes |
|-----------|--------|
| CYD ESP32-2432S028 | 68 × 50 mm display window |
| Jetson Nano 4GB + carrier | M2 standoffs in front shell |
| USB Wi‑Fi dongle | Route through rear vent slots |

## Print settings

| Setting | Value |
|---------|-------|
| Material | PETG (field) or PLA+ (bench prototype) |
| Layer height | 0.2 mm |
| Infill | 20% gyroid |
| Supports | Front shell — under display lip if needed |
| Brim | Rear shell — recommended |

### Orientation

| Part | Bed contact |
|------|-------------|
| Front shell | Internal/back face down |
| Rear shell | Outer back down |
| Clip / COD accessories | Flat |

## Assembly

1. Dry-fit front and rear at mid-depth (~15 mm seam).
2. Mount Jetson carrier on front-shell M2 standoffs; verify hole spacing for your carrier board.
3. Secure CYD module behind the 2.8" window (tape or 2 mm standoffs).
4. Place LiPo in rear tray; route USB-C through bottom slot.
5. Mate halves; press `mcb_clip` into side slots until snap.
6. Flash Jetson image and run `python main.py` in **authorized lab VLAN only**.

## COD STL + KSS pack

Digital buyers receive `cod_clip.stl` and `cod_wall_dock.stl` (generate with `--variant all`). Slicer profiles ship separately via checkout — not stored in this repo.

## Ecosystem

Enclosure geometry is independent of [CyberThreatGotchi](https://github.com/salvador-Data/cyberThreatGotchi) Tamagotchi shells (`hardware/stl/eink/`). CTG covers BPI-R3 Mini edge defense; CrackBot covers the **lab VLAN** wordlist workflow.
