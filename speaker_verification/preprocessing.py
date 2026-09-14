import io
import logging
import numpy as np
import scipy.signal
import soundfile as sf
import librosa
import torch

from speaker_verification.config import settings
from speaker_verification.exceptions import (
    EmptyAudioError,
    InvalidAudioError,
    CorruptedAudioError,
    InsufficientSpeechError,
)

logger = logging.getLogger(__name__)


def load_and_preprocess_audio(
    audio_bytes: bytes,
    target_sample_rate: int = settings.target_sample_rate,
    min_speech_duration: float = settings.min_speech_duration_sec,
) -> torch.Tensor:
    """
    Validates, decodes, resamples, and extracts speech activity from raw audio bytes.

    Pipeline:
    1. Validate input non-empty.
    2. Decode audio (soundfile / librosa fallback).
    3. Convert to mono.
    4. Resample to target_sample_rate (16000 Hz).
    5. Perform energy-based VAD / speech segment extraction.
    6. Ensure resulting speech duration >= min_speech_duration.
    7. Normalize amplitude to [-1.0, 1.0].

    Returns:
        torch.Tensor: Preprocessed 1D audio waveform tensor of shape (num_samples,).
    """
    if not audio_bytes or len(audio_bytes) == 0:
        raise EmptyAudioError("Received 0 bytes of audio data.")

    # 1. Decode raw audio bytes
    try:
        audio_stream = io.BytesIO(audio_bytes)
        try:
            waveform, orig_sr = sf.read(audio_stream, dtype="float32")
        except Exception:
            # Fallback to librosa for extended format support (MP3, OGG, FLAC)
            audio_stream.seek(0)
            waveform, orig_sr = librosa.load(audio_stream, sr=None, mono=False)
            if isinstance(waveform, np.ndarray) and waveform.ndim > 1:
                waveform = waveform.T # librosa loads channels first
    except Exception as exc:
        logger.warning(f"Audio decoding failure: {exc}")
        raise CorruptedAudioError(f"Failed to decode audio stream: {str(exc)}")

    if waveform is None or waveform.size == 0:
        raise EmptyAudioError("Decoded waveform contains 0 samples.")

    # 2. Convert stereo/multichannel to mono
    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)

    # Clean non-finite values (NaN, Inf)
    if not np.isfinite(waveform).all():
        waveform = np.nan_to_num(waveform, nan=0.0, posinf=0.0, neginf=0.0)

    # 3. Resample if necessary
    if orig_sr != target_sample_rate and orig_sr > 0:
        num_samples = int(round(len(waveform) * (target_sample_rate / orig_sr)))
        if num_samples > 0:
            waveform = scipy.signal.resample(waveform, num_samples).astype(np.float32)
        else:
            raise EmptyAudioError("Resampled waveform length is 0.")

    # 4. Energy-based Voice Activity Detection (VAD) & speech segment extraction
    speech_waveform = extract_speech_activity(
        waveform=waveform,
        sample_rate=target_sample_rate,
        top_db=25,
        frame_length_ms=30,
        hop_length_ms=10,
    )

    extracted_duration = len(speech_waveform) / target_sample_rate
    if extracted_duration < min_speech_duration:
        raise InsufficientSpeechError(
            duration=extracted_duration,
            min_required=min_speech_duration,
        )

    # 5. Amplitude normalization (peak scaling)
    max_val = np.max(np.abs(speech_waveform))
    if max_val > 1e-6:
        speech_waveform = speech_waveform / max_val

    return torch.from_numpy(speech_waveform).float()


def extract_speech_activity(
    waveform: np.ndarray,
    sample_rate: int = 16000,
    top_db: float = 25.0,
    frame_length_ms: int = 30,
    hop_length_ms: int = 10,
) -> np.ndarray:
    """
    Extracts speech segments by filtering silent and low-energy frames.
    """
    if len(waveform) == 0 or np.max(np.abs(waveform)) < 1e-4:
        return np.array([], dtype=np.float32)

    frame_length = int(sample_rate * frame_length_ms / 1000)
    hop_length = int(sample_rate * hop_length_ms / 1000)

    if len(waveform) < frame_length:
        # Audio shorter than one frame, return as is if non-silent
        return waveform if np.max(np.abs(waveform)) > 1e-4 else np.array([], dtype=np.float32)

    try:
        # Use librosa.effects.split to separate non-silent regions
        intervals = librosa.effects.split(
            waveform,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        if len(intervals) == 0:
            return np.array([], dtype=np.float32)
        
        speech_parts = [waveform[start:end] for start, end in intervals]
        return np.concatenate(speech_parts, axis=0)
    except Exception as exc:
        logger.debug(f"Energy VAD split fallback triggered: {exc}")
        # Fallback simple RMS thresholding
        rms = np.sqrt(np.mean(waveform ** 2))
        if rms < 1e-4:
            return np.array([], dtype=np.float32)
        return waveform
