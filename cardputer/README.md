# Mr. CrackBot AI — M5 Cardputer

QWERTY keyboard UI with **feature parity** to [Mr.-CrackBot-AI-CYD](https://github.com/salvador-Data/Mr.-CrackBot-AI-CYD) where hardware allows (Wi‑Fi/BLE/SD/portal/OTA).

| Control | Action |
|---------|--------|
| `w` / `;` | Up |
| `s` / `.` | Down |
| Enter | Select |
| `` ` `` | Back |
| `r` | Rescan / refresh |

## Build

```bash
cd cardputer
py -3 -m platformio run -e m5stack-crackbot
```

## Layout vs CYD

- **CYD** → touch grid (`Mr.-CrackBot-AI-CYD`)
- **Cardputer** → this folder (keyboard menus)
- **Jetson bench** → repo root Python (`main.py`)
