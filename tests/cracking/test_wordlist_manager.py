from cracking.wordlist_manager import WordlistManager


def test_generate_wordlist():
    manager = WordlistManager()
    path = manager.generate_wordlist({"ssid": "TestNetwork", "bssid_prefix": "00:11:22"})
    assert isinstance(path, str)
    assert path.endswith("generated.txt")
