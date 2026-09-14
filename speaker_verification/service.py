import logging
from typing import Optional

from speaker_verification.config import settings
from speaker_verification.exceptions import EnrollmentNotFoundError, SpeakerNotFoundError
from speaker_verification.preprocessing import load_and_preprocess_audio
from speaker_verification.model import ModelManager
from speaker_verification.embedding import EmbeddingStorage
from speaker_verification.similarity import cosine_similarity, calculate_confidence
from speaker_verification.schemas import (
    EnrollmentResponse,
    VerificationResponse,
    RiskEngineSignal,
    SpeakerStatusResponse,
)

logger = logging.getLogger(__name__)


class SpeakerVerificationService:
    """
    Main business logic service for Speaker Verification.
    Coordinates audio preprocessing, embedding extraction, secure persistence,
    cosine similarity comparison, and Risk Engine signal construction.
    """

    def __init__(
        self,
        storage: Optional[EmbeddingStorage] = None,
        threshold: float = settings.verification_threshold,
    ):
        self.storage = storage or EmbeddingStorage()
        self.threshold = threshold

    def enroll_speaker(self, speaker_id: str, audio_bytes: bytes) -> EnrollmentResponse:
        """
        Enrolls a speaker by extracting and securely persisting their ECAPA-TDNN voice vector.

        Args:
            speaker_id: Unique identifier for the speaker.
            audio_bytes: Raw audio byte content.

        Returns:
            EnrollmentResponse
        """
        clean_speaker_id = speaker_id.strip()
        if not clean_speaker_id:
            raise ValueError("speaker_id cannot be empty.")

        logger.info(f"Initiating speaker enrollment for speaker_id '{clean_speaker_id}'.")

        # 1. Preprocess audio & extract speech active waveform
        waveform_tensor = load_and_preprocess_audio(
            audio_bytes=audio_bytes,
            target_sample_rate=settings.target_sample_rate,
            min_speech_duration=settings.min_speech_duration_sec,
        )

        # 2. Extract ECAPA-TDNN embedding vector via singleton ModelManager
        model = ModelManager.get_model()
        raw_embedding = model.extract_embedding(waveform_tensor)

        # 3. Securely persist normalized embedding
        self.storage.save_speaker_embedding(clean_speaker_id, raw_embedding)

        return EnrollmentResponse(
            speaker_id=clean_speaker_id,
            status="enrolled",
            message=f"Speaker '{clean_speaker_id}' successfully enrolled.",
        )

    def verify_speaker(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        threshold_override: Optional[float] = None,
    ) -> VerificationResponse:
        """
        Verifies whether an incoming audio sample matches an enrolled genuine speaker.

        Args:
            speaker_id: Enrolled speaker ID to compare against.
            audio_bytes: Incoming call raw audio bytes.
            threshold_override: Optional custom threshold to override global setting.

        Returns:
            VerificationResponse
        """
        clean_speaker_id = speaker_id.strip()
        if not clean_speaker_id:
            raise ValueError("speaker_id cannot be empty.")

        # 1. Ensure speaker is enrolled
        if not self.storage.speaker_exists(clean_speaker_id):
            raise SpeakerNotFoundError(speaker_id=clean_speaker_id)

        enrolled_embedding = self.storage.load_speaker_embedding(clean_speaker_id)

        # 2. Preprocess incoming audio
        incoming_waveform = load_and_preprocess_audio(
            audio_bytes=audio_bytes,
            target_sample_rate=settings.target_sample_rate,
            min_speech_duration=settings.min_speech_duration_sec,
        )

        # 3. Extract incoming ECAPA-TDNN embedding
        model = ModelManager.get_model()
        incoming_embedding = model.extract_embedding(incoming_waveform)

        # 4. Calculate Cosine Similarity & decision boundary
        active_threshold = threshold_override if threshold_override is not None else self.threshold
        similarity = cosine_similarity(enrolled_embedding, incoming_embedding)
        verified = bool(similarity >= active_threshold)

        # 5. Compute decision confidence metric
        confidence = calculate_confidence(similarity_score=similarity, threshold=active_threshold)

        logger.info(
            f"Verification executed for speaker_id '{clean_speaker_id}': "
            f"verified={verified}, similarity={similarity:.4f}, threshold={active_threshold:.4f}, confidence={confidence:.4f}"
        )

        return VerificationResponse(
            speaker_id=clean_speaker_id,
            verified=verified,
            similarity_score=round(similarity, 4),
            threshold=round(active_threshold, 4),
            confidence=confidence,
            model="ECAPA-TDNN",
        )

    def get_risk_signal(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        threshold_override: Optional[float] = None,
    ) -> RiskEngineSignal:
        """
        Produces a machine-readable payload for Nexora Risk Decision Engine.
        Meets Requirement 10.
        """
        verif_res = self.verify_speaker(
            speaker_id=speaker_id,
            audio_bytes=audio_bytes,
            threshold_override=threshold_override,
        )

        return RiskEngineSignal(
            signal="speaker_verification",
            speaker_verified=verif_res.verified,
            similarity_score=verif_res.similarity_score,
            confidence=verif_res.confidence,
        )

    def get_speaker_status(self, speaker_id: str) -> SpeakerStatusResponse:
        """Returns enrollment status for a speaker ID."""
        clean_id = speaker_id.strip()
        is_enrolled = self.storage.speaker_exists(clean_id)
        return SpeakerStatusResponse(
            speaker_id=clean_id,
            enrolled=is_enrolled,
        )

    def delete_speaker(self, speaker_id: str) -> bool:
        """Deletes enrollment record for a speaker ID."""
        return self.storage.delete_speaker(speaker_id)
