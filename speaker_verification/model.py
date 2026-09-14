import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import torch

from speaker_verification.config import settings
from speaker_verification.exceptions import ModelLoadingError, InferenceError

logger = logging.getLogger(__name__)


class BaseSpeakerModel(ABC):
    """Abstract interface for speaker embedding extractor model."""

    @abstractmethod
    def extract_embedding(self, waveform: torch.Tensor) -> np.ndarray:
        """
        Extract raw 192-dimensional ECAPA-TDNN speaker embedding vector.

        Args:
            waveform: 1D torch.Tensor float32 audio signal (16kHz mono).

        Returns:
            np.ndarray: 1D numpy array of shape (192,).
        """
        pass


class ECAPATDNNModel(BaseSpeakerModel):
    """
    Production ECAPA-TDNN speaker embedding extractor utilizing SpeechBrain.
    Model: speechbrain/spkrec-ecapa-voxceleb
    """

    def __init__(self, model_source: str = settings.model_name, device: str = settings.device):
        self.model_source = model_source
        self.device = device
        self.classifier = None
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading ECAPA-TDNN pretrained model from '{self.model_source}' on device '{self.device}'...")
            
            # Compatible SpeechBrain imports (handles v0.5 and v1.0+)
            try:
                from speechbrain.inference.speaker import EncoderClassifier
            except ImportError:
                from speechbrain.pretrained import EncoderClassifier

            self.classifier = EncoderClassifier.from_hparams(
                source=self.model_source,
                run_opts={"device": self.device},
            )
            logger.info("ECAPA-TDNN model loaded successfully.")
        except Exception as exc:
            logger.error(f"Failed to load SpeechBrain ECAPA-TDNN model: {exc}")
            raise ModelLoadingError(f"Could not load ECAPA-TDNN model from {self.model_source}: {str(exc)}")

    def extract_embedding(self, waveform: torch.Tensor) -> np.ndarray:
        if self.classifier is None:
            raise ModelLoadingError("ECAPA-TDNN model is not loaded.")

        try:
            # Ensure 2D tensor batch shape (1, num_samples)
            if waveform.ndim == 1:
                waveform = waveform.unsqueeze(0)

            waveform = waveform.to(self.device)

            with torch.no_grad():
                # Extract embedding tensor from SpeechBrain model
                embeddings = self.classifier.encode_batch(waveform)
                # Squeeze to 1D numpy vector (192,)
                embedding_np = embeddings.squeeze().cpu().numpy()

            if embedding_np.ndim != 1 or len(embedding_np) == 0:
                raise InferenceError(f"Unexpected embedding output shape: {embedding_np.shape}")

            return embedding_np.astype(np.float32)
        except Exception as exc:
            logger.error(f"Inference failure during ECAPA-TDNN embedding extraction: {exc}")
            raise InferenceError(f"Inference execution failed: {str(exc)}")


class MockECAPATDNNModel(BaseSpeakerModel):
    """
    Isolated development & fast offline unit test mock model.
    Generates deterministic 192-dimensional embeddings based on audio signal characteristics.
    """

    def __init__(self, embedding_dim: int = 192):
        self.embedding_dim = embedding_dim
        logger.info(f"Initialized MockECAPATDNNModel (dim={embedding_dim}) for testing/development.")

    def extract_embedding(self, waveform: torch.Tensor) -> np.ndarray:
        try:
            # Generate deterministic pseudo-embedding based on waveform values
            arr = waveform.cpu().numpy()
            # Compute a hash of array summary statistics to create deterministic features
            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr))
            first_vals = arr[:10].tobytes() if len(arr) >= 10 else arr.tobytes()
            seed_hash = int(hashlib.md5(first_vals).hexdigest(), 16) % (2**32)

            rng = np.random.RandomState(seed_hash)
            # Create synthetic feature vector influenced by audio properties
            vec = rng.randn(self.embedding_dim).astype(np.float32)
            vec[0] += mean_val * 10.0
            vec[1] += std_val * 10.0
            
            # L2 normalize mock vector
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec
        except Exception as exc:
            raise InferenceError(f"Mock inference failure: {str(exc)}")


class ModelManager:
    """
    Singleton lifecycle manager for the ECAPA-TDNN speaker model.
    Ensures model is loaded once and reused across all incoming requests.
    """
    _instance: Optional[BaseSpeakerModel] = None

    @classmethod
    def get_model(cls) -> BaseSpeakerModel:
        if cls._instance is None:
            cls.initialize_model()
        return cls._instance

    @classmethod
    def initialize_model(cls, force_mock: bool = False) -> BaseSpeakerModel:
        if force_mock or settings.use_mock_model:
            logger.info("Initializing ModelManager with MockECAPATDNNModel (Mock Mode enabled).")
            cls._instance = MockECAPATDNNModel()
        else:
            logger.info("Initializing ModelManager with production SpeechBrain ECAPATDNNModel.")
            cls._instance = ECAPATDNNModel()
        return cls._instance

    @classmethod
    def set_model(cls, model_instance: BaseSpeakerModel):
        """Allows injecting a custom or mock model instance (e.g. for PyTest fixtures)."""
        cls._instance = model_instance
