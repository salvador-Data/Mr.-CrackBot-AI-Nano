import os
from pathlib import Path

from main import use_combined_wordlist


def test_use_combined_wordlist():
    combined_wordlist_path = Path("data/wordlists/RockYou2024_combined.txt")
    combined_wordlist_path.parent.mkdir(parents=True, exist_ok=True)
    combined_wordlist_path.write_text("password1\npassword2\n", encoding="utf-8")

    result = Path(use_combined_wordlist())
    assert result == combined_wordlist_path
    assert result.is_file()

    combined_wordlist_path.unlink(missing_ok=True)
