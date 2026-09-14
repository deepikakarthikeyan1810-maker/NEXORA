import logging
import os
from pathlib import Path
import numpy as np

from speaker_verification.config import settings
from speaker_verification.exceptions import EnrollmentNotFoundError, SpeakerNotFoundError
from speaker_verification.similarity import normalize_embedding

logger = logging.getLogger(__name__)


class EmbeddingStorage:
    """
    Secure storage and retrieval system for speaker biometric embedding vectors.
    Strictly handles normalized numpy embedding arrays without storing raw voice recordings.
    """

    def __init__(self, storage_dir: Path = settings.storage_dir):
        self.storage_dir = Path(storage_dir)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """Creates storage directory with restricted directory permissions if not present."""
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            try:
                os.chmod(self.storage_dir, 0o700) # Owner read/write/execute only
            except Exception as exc:
                logger.warning(f"Could not set restrictive permissions on storage dir: {exc}")

    def _get_speaker_filepath(self, speaker_id: str) -> Path:
        """Sanitizes speaker_id and constructs secure destination filepath."""
        # Sanitize speaker_id to prevent directory traversal attacks
        safe_id = "".join(c for c in speaker_id if c.isalnum() or c in ("-", "_")).strip()
        if not safe_id:
            raise ValueError(f"Invalid speaker_id format: '{speaker_id}'")
        return self.storage_dir / f"{safe_id}.npy"

    def save_speaker_embedding(self, speaker_id: str, embedding: np.ndarray) -> Path:
        """
        L2-normalizes and saves speaker embedding to disk with secure 0o600 permissions.
        Does NOT log raw embedding values or sensitive personal identifiers.
        """
        filepath = self._get_speaker_filepath(speaker_id)
        normalized_emb = normalize_embedding(embedding)

        # Write to temporary file first then atomic rename
        temp_path = filepath.with_suffix(".tmp.npy")
        try:
            np.save(temp_path, normalized_emb)
            os.chmod(temp_path, 0o600) # Restricted owner read/write
            temp_path.replace(filepath)
            logger.info(f"Successfully saved enrollment embedding for speaker_id '{speaker_id}'.")
            return filepath
        except Exception as exc:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            logger.error(f"Failed to persist embedding for speaker_id '{speaker_id}': {exc}")
            raise IOError(f"Could not securely save speaker embedding: {str(exc)}")

    def load_speaker_embedding(self, speaker_id: str) -> np.ndarray:
        """
        Loads enrolled speaker embedding vector from disk.
        """
        filepath = self._get_speaker_filepath(speaker_id)
        if not filepath.exists():
            raise EnrollmentNotFoundError(speaker_id=speaker_id)

        try:
            embedding = np.load(filepath)
            if not isinstance(embedding, np.ndarray) or embedding.size == 0:
                raise ValueError("Loaded embedding is empty or invalid shape.")
            return normalize_embedding(embedding)
        except Exception as exc:
            logger.error(f"Failed to load embedding file for speaker '{speaker_id}': {exc}")
            raise EnrollmentNotFoundError(speaker_id=speaker_id)

    def speaker_exists(self, speaker_id: str) -> bool:
        """Checks if a speaker is currently enrolled."""
        try:
            filepath = self._get_speaker_filepath(speaker_id)
            return filepath.exists()
        except ValueError:
            return False

    def delete_speaker(self, speaker_id: str) -> bool:
        """Deletes enrolled speaker embedding record."""
        try:
            filepath = self._get_speaker_filepath(speaker_id)
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted enrollment record for speaker '{speaker_id}'.")
                return True
            raise SpeakerNotFoundError(speaker_id=speaker_id)
        except ValueError:
            raise SpeakerNotFoundError(speaker_id=speaker_id)
