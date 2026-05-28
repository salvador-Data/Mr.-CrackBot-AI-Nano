from cracking.hashcat_wrapper import crack_password


def test_crack_password(monkeypatch):
    class FakeProcess:
        def __init__(self):
            self.stdout = iter(["Progress: 50%\n", "Cracked: testpass\n"])

        def wait(self):
            return 0

    def mock_popen(*args, **kwargs):
        assert args[0][0] == "hashcat"
        return FakeProcess()

    monkeypatch.setattr("cracking.hashcat_wrapper.subprocess.Popen", mock_popen)
    crack_password("test.hccapx", "test_wordlist.txt", progress_callback=lambda v: None)
