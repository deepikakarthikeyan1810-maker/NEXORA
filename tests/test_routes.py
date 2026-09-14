from fastapi.testclient import TestClient


def test_enroll_route_success(test_client: TestClient, sample_speaker_a_audio):
    """Test POST /speaker/enroll endpoint."""
    files = {"file": ("speaker_a.wav", sample_speaker_a_audio, "audio/wav")}
    data = {"speaker_id": "api_user_101"}

    response = test_client.post("/speaker/enroll", data=data, files=files)
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["speaker_id"] == "api_user_101"
    assert json_resp["status"] == "enrolled"


def test_verify_route_success(test_client: TestClient, sample_speaker_a_audio, sample_speaker_a_same_audio):
    """Test POST /speaker/verify endpoint."""
    # First enroll
    files_enroll = {"file": ("speaker_a.wav", sample_speaker_a_audio, "audio/wav")}
    test_client.post("/speaker/enroll", data={"speaker_id": "api_user_202"}, files=files_enroll)

    # Now verify
    files_verif = {"file": ("speaker_a_verify.wav", sample_speaker_a_same_audio, "audio/wav")}
    response = test_client.post("/speaker/verify", data={"speaker_id": "api_user_202"}, files=files_verif)

    assert response.status_code == 200
    res = response.json()
    assert res["speaker_id"] == "api_user_202"
    assert res["verified"] is True
    assert "similarity_score" in res
    assert "confidence" in res
    assert res["model"] == "ECAPA-TDNN"


def test_verify_unknown_speaker_404(test_client: TestClient, sample_speaker_a_audio):
    """Test verification for unknown speaker returns HTTP 404."""
    files = {"file": ("sample.wav", sample_speaker_a_audio, "audio/wav")}
    response = test_client.post("/speaker/verify", data={"speaker_id": "ghost_speaker"}, files=files)

    assert response.status_code == 404
    json_err = response.json()
    assert json_err["error_code"] == "SPEAKER_NOT_FOUND"


def test_enroll_empty_audio_400(test_client: TestClient, empty_audio_bytes):
    """Test uploading empty audio returns HTTP 400."""
    files = {"file": ("empty.wav", empty_audio_bytes, "audio/wav")}
    response = test_client.post("/speaker/enroll", data={"speaker_id": "empty_user"}, files=files)

    assert response.status_code == 400
    json_err = response.json()
    assert json_err["error_code"] == "EMPTY_AUDIO"


def test_enroll_corrupted_audio_400(test_client: TestClient, corrupted_audio_bytes):
    """Test uploading corrupted audio returns HTTP 400."""
    files = {"file": ("bad.wav", corrupted_audio_bytes, "audio/wav")}
    response = test_client.post("/speaker/enroll", data={"speaker_id": "bad_user"}, files=files)

    assert response.status_code == 400
    json_err = response.json()
    assert json_err["error_code"] == "CORRUPTED_AUDIO"


def test_get_speaker_status_route(test_client: TestClient, sample_speaker_a_audio):
    """Test GET /speaker/{speaker_id} endpoint."""
    speaker_id = "user_status_check_fresh_99"
    response = test_client.get(f"/speaker/{speaker_id}")
    assert response.status_code == 200
    assert response.json()["enrolled"] is False

    # Enroll
    test_client.post("/speaker/enroll", data={"speaker_id": speaker_id}, files={"file": ("a.wav", sample_speaker_a_audio, "audio/wav")})

    response_after = test_client.get(f"/speaker/{speaker_id}")
    assert response_after.status_code == 200
    assert response_after.json()["enrolled"] is True


def test_risk_signal_route(test_client: TestClient, sample_speaker_a_audio):
    """Test POST /speaker/risk-signal endpoint."""
    # Enroll
    test_client.post("/speaker/enroll", data={"speaker_id": "risk_user_1"}, files={"file": ("a.wav", sample_speaker_a_audio, "audio/wav")})

    # Risk Signal
    response = test_client.post("/speaker/risk-signal", data={"speaker_id": "risk_user_1"}, files={"file": ("a.wav", sample_speaker_a_audio, "audio/wav")})
    assert response.status_code == 200
    payload = response.json()
    assert payload["signal"] == "speaker_verification"
    assert payload["speaker_verified"] is True
    assert "similarity_score" in payload
    assert "confidence" in payload
