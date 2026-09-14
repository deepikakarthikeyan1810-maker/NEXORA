import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for Speaker Verification module.
    Threshold and storage paths are fully configurable via environment variables.
    """
    model_config = SettingsConfigDict(env_prefix="SPEAKER_", case_sensitive=False)

    verification_threshold: float = float(os.getenv("SPEAKER_VERIFICATION_THRESHOLD", "0.70"))
    target_sample_rate: int = 16000
    min_speech_duration_sec: float = 0.5
    max_audio_duration_sec: float = 300.0
    storage_dir: Path = Path(os.getenv("SPEAKER_EMBEDDING_DIR", "./data/embeddings"))
    model_name: str = os.getenv("SPEAKER_MODEL_NAME", "speechbrain/spkrec-ecapa-voxceleb")
    use_mock_model: bool = os.getenv("USE_MOCK_MODEL", "false").lower() in ("true", "1", "t")
    device: str = os.getenv("SPEAKER_MODEL_DEVICE", "cpu")


settings = Settings()
