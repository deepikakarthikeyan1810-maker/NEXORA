"""
Domain-specific exceptions for Nexora Speaker Verification.
"""

class SpeakerVerificationError(Exception):
    """Base exception for speaker verification errors."""
    def __init__(self, message: str, code: str = "SPEAKER_VERIFICATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class SpeakerNotFoundError(SpeakerVerificationError):
    """Raised when a requested speaker_id does not exist."""
    def __init__(self, speaker_id: str):
        super().__init__(f"Speaker ID '{speaker_id}' is not enrolled.", code="SPEAKER_NOT_FOUND")
        self.speaker_id = speaker_id


class EnrollmentNotFoundError(SpeakerVerificationError):
    """Raised when enrollment embedding is missing for a speaker."""
    def __init__(self, speaker_id: str):
        super().__init__(f"No enrollment record found for speaker ID '{speaker_id}'.", code="ENROLLMENT_NOT_FOUND")
        self.speaker_id = speaker_id


class InvalidAudioError(SpeakerVerificationError):
    """Raised when the audio format is unsupported or corrupted."""
    def __init__(self, message: str = "Invalid or unsupported audio file format."):
        super().__init__(message, code="INVALID_AUDIO")


class EmptyAudioError(SpeakerVerificationError):
    """Raised when the provided audio file contains 0 bytes or zero samples."""
    def __init__(self, message: str = "Audio file is empty or contains zero samples."):
        super().__init__(message, code="EMPTY_AUDIO")


class InsufficientSpeechError(SpeakerVerificationError):
    """Raised when audio does not contain sufficient voice activity/speech segments."""
    def __init__(self, duration: float, min_required: float):
        super().__init__(
            f"Audio contains insufficient speech activity ({duration:.2f}s extracted, minimum required is {min_required:.2f}s).",
            code="INSUFFICIENT_SPEECH"
        )
        self.duration = duration
        self.min_required = min_required


class CorruptedAudioError(SpeakerVerificationError):
    """Raised when audio file decoding fails due to corruption."""
    def __init__(self, message: str = "Audio file data is corrupted and cannot be decoded."):
        super().__init__(message, code="CORRUPTED_AUDIO")


class ModelLoadingError(SpeakerVerificationError):
    """Raised when loading the ECAPA-TDNN model fails."""
    def __init__(self, message: str = "Failed to load ECAPA-TDNN speaker model."):
        super().__init__(message, code="MODEL_LOADING_FAILURE")


class InferenceError(SpeakerVerificationError):
    """Raised when model forward pass or embedding extraction fails."""
    def __init__(self, message: str = "Failed to generate speaker embedding from audio tensor."):
        super().__init__(message, code="INFERENCE_FAILURE")
