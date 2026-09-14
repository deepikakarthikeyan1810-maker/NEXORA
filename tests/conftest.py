import io
import shutil
import tempfile
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from speaker_verification.config import settings
from speaker_verification.model import ModelManager, MockECAPATDNNModel
from speaker_verification.embedding import EmbeddingStorage
from speaker_verification.service import SpeakerVerificationService
from app import app


def generate_sine_wav_bytes(frequency: float = 440.0, duration: float = 2.0, sample_rate: int = 16000) -> bytes:
    """Generates synthetic audio WAV bytes for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Generate audio signal with harmonics
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t) + 0.25 * np.sin(2 * np.pi * (frequency * 2) * t)
    waveform = waveform.astype(np.float32)
    
    bio = io.BytesIO()
    sf.write(bio, waveform, sample_rate, format="WAV")
    return bio.getvalue()


@pytest.fixture(autouse=True)
def setup_mock_model_and_temp_storage(monkeypatch):
    """
    Globally configures MockECAPATDNNModel and isolated temporary storage for all unit tests.
    Ensures unit tests are fast, deterministic, and 100% offline.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="nexora_test_embeddings_"))
    monkeypatch.setattr(settings, "storage_dir", temp_dir)
    monkeypatch.setattr(settings, "use_mock_model", True)
    
    mock_instance = MockECAPATDNNModel()
    ModelManager.set_model(mock_instance)
    
    yield temp_dir
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_speaker_a_audio():
    return generate_sine_wav_bytes(frequency=440.0, duration=2.0)


@pytest.fixture
def sample_speaker_a_same_audio():
    return generate_sine_wav_bytes(frequency=440.0, duration=2.0)


@pytest.fixture
def sample_speaker_b_audio():
    return generate_sine_wav_bytes(frequency=1200.0, duration=2.0)


@pytest.fixture
def empty_audio_bytes():
    return b""


@pytest.fixture
def corrupted_audio_bytes():
    return b"CORRUPTED_AUDIO_DATA_STREAM_HEADER_INVALID_12345"


@pytest.fixture
def test_client():
    return TestClient(app)
