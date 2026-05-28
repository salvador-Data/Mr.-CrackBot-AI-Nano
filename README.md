![MrCrackBotAI](docs/screenshots/mrcatbar2.webp)

# Mr. CrackBot AI Nano

**Status:** Early development — lab/simulation mode works on Windows and Linux CI; Jetson hardware path requires monitor-mode Wi‑Fi tools.

Mr. CrackBot AI Nano is a Jetson Nano–oriented project for **authorized** Wi‑Fi security research: handshake capture, wordlist generation, and GPU hashcat cracking. Use only on networks you own or have written permission to test.

## Features (target)

- Heuristic + optional AI wordlist generation (`MR_CRACKBOT_USE_AI=1` + `requirements-jetson.txt`)
- WPA handshake capture workflow (airodump-ng / aireplay-ng on Linux)
- Hashcat integration for GPU cracking on Jetson
- Pygame intro + Tk control UI

## Quick start (simulation — no Wi‑Fi hardware)

```bash
git clone https://github.com/salvadordata/Mr.-CrackBot-AI-Nano.git
cd Mr.-CrackBot-AI-Nano
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -v
python main.py --simulation --skip-intro --headless
```

## Jetson / GPU (optional AI)

```bash
pip install -r requirements-jetson.txt
export MR_CRACKBOT_USE_AI=1
python main.py --skip-intro
```

## Hardware

See the bill of materials in this README’s history: Jetson Nano 4GB, USB Wi‑Fi adapter (monitor mode), touchscreen, and battery pack.

## Wordlists

`setup.py` can download and merge RockYou2024 archives (Mega links in script). This is **optional** and requires `megatools` + `p7zip-full` on Linux:

```bash
python setup.py
```

## Legal

Educational and authorized testing only. The authors are not responsible for misuse.

## Contributing

Open an issue or PR on [GitHub](https://github.com/salvadordata/Mr.-CrackBot-AI-Nano).
