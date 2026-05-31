# Security & authorized use — Mr. CrackBot AI Nano

## Scope

Mr. CrackBot AI Nano provides **authorized** Wi‑Fi security research tooling:

- Wordlist generation (heuristic + optional AI)
- Handshake capture workflows (Linux / Jetson)
- GPU hashcat integration
- Companion field firmware (CYD and Cardputer repos)

## Authorized use only

Operate only on:

- Networks and devices **you own**
- Assets covered by a **signed rules-of-engagement** or written permission
- Isolated **lab VLAN** segments — never production or third-party networks without authorization

## You must not

- Deploy against neighbors, public Wi‑Fi, employers, or clients without explicit authorization
- Exfiltrate handshakes or credentials outside your lab retention policy
- Ship pre-flashed units without Hacker Planet LLC lab-use documentation

## Secrets & logging

- Do not commit API keys, wordlist archives with live credentials, or customer ROE documents
- `mr_crackbot_ai.log` and SD exports may contain sensitive data — restrict filesystem permissions
- Simulation mode (`MR_CRACKBOT_SIMULATION=1`) is preferred for CI and public demos

## Field firmware

CYD and Cardputer firmware expose real Wi‑Fi/BLE lab capabilities. Security policy for those targets:

- [Mr.-CrackBot-AI-CYD SECURITY.md](https://github.com/salvador-Data/Mr.-CrackBot-AI-CYD/blob/main/SECURITY.md)

## Reporting

Security issues: **salvadorData@proton.me** (Hacker Planet LLC). Do not file public issues with exploit chains against non-lab targets.

## Feature preservation policy

Hacker Planet does **not** remove attack-surface features from lab repos for “safety through omission.” Distribution is gated by **lawful use documentation**, not feature stripping.
