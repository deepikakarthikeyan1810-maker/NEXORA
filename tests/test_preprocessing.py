import io
import numpy as np
import pytest
import soundfile as sf
import torch

from speaker_verification.preprocessing import load_and_preprocess_audio
from speaker_verification.exceptions import (
    EmptyAudioError,
    CorruptedAudioError,
    InsufficientSpeechError,
)


def test_valid_audio_preprocessing(sample_speaker_a_audio):
    """Test successful loading, resampling, and VAD processing of valid audio."""
    waveform = load_and_preprocess_audio(sample_speaker_a_audio, target_sample_rate=16000, min_speech_duration=0.5)
    
    assert isinstance(waveform, torch.Tensor)
    assert waveform.ndim == 1
    assert len(waveform) >= 16000 * 0.5 # At least 0.5 sec of samples
    assert float(torch.max(torch.abs(waveform))) <= 1.0


def test_empty_audio_raises_error():
    """Test handling of 0 byte audio input."""
    with pytest.raises(EmptyAudioError):
        load_and_preprocess_audio(b"", target_sample_rate=16000)


def test_corrupted_audio_raises_error(corrupted_audio_bytes):
    """Test handling of corrupted audio file bytes."""
    with pytest.raises(CorruptedAudioError):
        load_and_preprocess_audio(corrupted_audio_bytes, target_sample_rate=16000)


def test_insufficient_speech_raises_error():
    """Test handling of audio containing pure silence (VAD strips all samples)."""
    # Create 2 seconds of pure silence
    silent_audio = np.zeros(16000 * 2, dtype=np.float32)
    bio = io.BytesIO()
    sf.write(bio, silent_audio, 16000, format="WAV")
    silent_bytes = bio.getvalue()

    with pytest.raises(InsufficientSpeechError) as exc_info:
        load_and_preprocess_audio(silent_bytes, target_sample_rate=16000, min_speech_duration=0.5)
    
    assert exc_info.value.code == "INSUFFICIENT_SPEECH"
    assert exc_info.value.min_required == 0.5
