from __future__ import annotations

from pathlib import Path

from ai.password_model import PasswordGenerator


class WordlistManager:
    def __init__(self) -> None:
        self.generator = PasswordGenerator()

    def generate_wordlist(self, features: dict) -> str:
        ssid = features.get("ssid", "network")
        bssid_prefix = features.get("bssid_prefix", "00:11:22")
        prompt = f"SSID: {ssid}, BSSID: {bssid_prefix}"
        words = self.generator.generate(prompt)
        wordlist_path = Path("data/wordlists/generated.txt")
        wordlist_path.parent.mkdir(parents=True, exist_ok=True)
        wordlist_path.write_text("\n".join(words), encoding="utf-8")
        return str(wordlist_path)
