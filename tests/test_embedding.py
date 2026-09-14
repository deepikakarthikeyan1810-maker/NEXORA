import os
import numpy as np
import pytest

from speaker_verification.embedding import EmbeddingStorage
from speaker_verification.exceptions import EnrollmentNotFoundError, SpeakerNotFoundError


def test_save_and_load_embedding(setup_mock_model_and_temp_storage):
    """Test saving and loading speaker embedding vector."""
    storage = EmbeddingStorage(storage_dir=setup_mock_model_and_temp_storage)
    speaker_id = "user_test_001"
    embedding = np.random.randn(192).astype(np.float32)

    saved_path = storage.save_speaker_embedding(speaker_id, embedding)
    assert saved_path.exists()

    # Verify restrictive permissions (0o600)
    file_mode = os.stat(saved_path).st_mode & 0o777
    assert file_mode in (0o600, 0o700)

    loaded_emb = storage.load_speaker_embedding(speaker_id)
    assert loaded_emb.shape == (192,)
    # Verify loaded vector is L2 normalized
    assert pytest.approx(np.linalg.norm(loaded_emb), abs=1e-5) == 1.0


def test_load_nonexistent_speaker_raises_error(setup_mock_model_and_temp_storage):
    """Test loading non-existent speaker raises EnrollmentNotFoundError."""
    storage = EmbeddingStorage(storage_dir=setup_mock_model_and_temp_storage)
    with pytest.raises(EnrollmentNotFoundError) as exc_info:
        storage.load_speaker_embedding("nonexistent_user_999")
    
    assert exc_info.value.code == "ENROLLMENT_NOT_FOUND"


def test_speaker_exists_and_delete(setup_mock_model_and_temp_storage):
    """Test speaker_exists check and delete_speaker operation."""
    storage = EmbeddingStorage(storage_dir=setup_mock_model_and_temp_storage)
    speaker_id = "user_delete_test"
    embedding = np.ones(192, dtype=np.float32)

    assert not storage.speaker_exists(speaker_id)
    storage.save_speaker_embedding(speaker_id, embedding)
    assert storage.speaker_exists(speaker_id)

    res = storage.delete_speaker(speaker_id)
    assert res is True
    assert not storage.speaker_exists(speaker_id)

    with pytest.raises(SpeakerNotFoundError):
        storage.delete_speaker(speaker_id)


def test_invalid_speaker_id_traversal_sanitization(setup_mock_model_and_temp_storage):
    """Test path traversal protection in speaker_id formatting."""
    storage = EmbeddingStorage(storage_dir=setup_mock_model_and_temp_storage)
    unsafe_id = "../../etc/passwd"
    embedding = np.ones(192, dtype=np.float32)

    saved_path = storage.save_speaker_embedding(unsafe_id, embedding)
    # Ensure saved path remains strictly inside designated storage directory
    assert setup_mock_model_and_temp_storage in saved_path.parents
    assert saved_path.name == "etcpasswd.npy"
