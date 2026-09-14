import pytest

from speaker_verification.service import SpeakerVerificationService
from speaker_verification.exceptions import SpeakerNotFoundError


def test_enrollment_success(sample_speaker_a_audio):
    """Test enrolling a speaker with valid audio."""
    service = SpeakerVerificationService(threshold=0.70)
    res = service.enroll_speaker("speaker_alpha", sample_speaker_a_audio)

    assert res.speaker_id == "speaker_alpha"
    assert res.status == "enrolled"
    assert "successfully enrolled" in res.message


def test_verification_genuine_speaker(sample_speaker_a_audio, sample_speaker_a_same_audio):
    """Test verification of genuine enrolled speaker matches."""
    service = SpeakerVerificationService(threshold=0.70)
    service.enroll_speaker("speaker_genuine", sample_speaker_a_audio)

    verif = service.verify_speaker("speaker_genuine", sample_speaker_a_same_audio)
    assert verif.speaker_id == "speaker_genuine"
    assert verif.verified is True
    assert verif.similarity_score >= 0.70
    assert verif.confidence >= 0.50
    assert verif.model == "ECAPA-TDNN"


def test_verification_imposter_rejection(sample_speaker_a_audio, sample_speaker_b_audio):
    """Test rejection of a different imposter speaker."""
    service = SpeakerVerificationService(threshold=0.70)
    service.enroll_speaker("speaker_owner", sample_speaker_a_audio)

    verif = service.verify_speaker("speaker_owner", sample_speaker_b_audio)
    assert verif.speaker_id == "speaker_owner"
    assert verif.verified is False
    assert verif.similarity_score < 0.70


def test_verification_unknown_speaker(sample_speaker_a_audio):
    """Test verification for an un-enrolled speaker raises SpeakerNotFoundError."""
    service = SpeakerVerificationService(threshold=0.70)
    with pytest.raises(SpeakerNotFoundError) as exc_info:
        service.verify_speaker("unknown_speaker_404", sample_speaker_a_audio)

    assert exc_info.value.code == "SPEAKER_NOT_FOUND"


def test_verification_threshold_override(sample_speaker_a_audio, sample_speaker_a_same_audio):
    """Test dynamic threshold overriding."""
    service = SpeakerVerificationService(threshold=0.70)
    service.enroll_speaker("speaker_thresh_test", sample_speaker_a_audio)

    # Impossible threshold (1.001) should reject even perfect 1.0 similarity score
    strict_res = service.verify_speaker("speaker_thresh_test", sample_speaker_a_same_audio, threshold_override=1.001)
    assert strict_res.threshold == 1.001
    assert strict_res.verified is False

    # Lenient 0.10 threshold should accept
    lenient_res = service.verify_speaker("speaker_thresh_test", sample_speaker_a_same_audio, threshold_override=0.10)
    assert lenient_res.threshold == 0.10
    assert lenient_res.verified is True


def test_risk_engine_signal(sample_speaker_a_audio):
    """Test production of Risk Engine signal payload."""
    service = SpeakerVerificationService(threshold=0.70)
    service.enroll_speaker("speaker_risk_test", sample_speaker_a_audio)

    signal = service.get_risk_signal("speaker_risk_test", sample_speaker_a_audio)
    assert signal.signal == "speaker_verification"
    assert signal.speaker_verified is True
    assert isinstance(signal.similarity_score, float)
    assert isinstance(signal.confidence, float)
