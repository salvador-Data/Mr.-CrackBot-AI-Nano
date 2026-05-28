from network.handshake import capture_handshake


def test_capture_handshake():
    result = capture_handshake("mock_bssid", "6")
    assert result.endswith(".cap")
