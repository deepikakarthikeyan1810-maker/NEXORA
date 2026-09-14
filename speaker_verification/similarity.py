import numpy as np


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    Applies L2 normalization to a 1D speaker embedding vector.

    v_norm = v / ||v||_2

    Args:
        embedding: 1D numpy array.

    Returns:
        np.ndarray: L2-normalized 1D numpy array.
    """
    norm = np.linalg.norm(embedding)
    if norm < 1e-12:
        return embedding.astype(np.float32)
    return (embedding / norm).astype(np.float32)


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Computes Cosine Similarity between two speaker embedding vectors.

    Cosine Similarity = (u · v) / (||u||_2 * ||v||_2)

    For pre-normalized L2 vectors, this simplifies to dot product (u · v).

    Args:
        embedding1: 1D numpy array of shape (N,).
        embedding2: 1D numpy array of shape (N,).

    Returns:
        float: Cosine similarity score bounded in [-1.0, 1.0].
    """
    u = normalize_embedding(embedding1)
    v = normalize_embedding(embedding2)

    sim = float(np.dot(u, v))
    # Clamp to valid [-1.0, 1.0] float range to handle numerical precision noise
    return max(-1.0, min(1.0, sim))


def calculate_confidence(similarity_score: float, threshold: float) -> float:
    """
    Calculates a normalized decision confidence score derived from the similarity score.

    ---
    CONCEPTUAL DISTINCTION:
    - SIMILARITY SCORE: The direct geometric cosine angle dot-product between two high-dimensional
      ECAPA-TDNN embedding vectors (range: [-1.0, 1.0]). Represents feature vector proximity.
    - CONFIDENCE LEVEL: A calibrated metric (range: [0.0, 1.0]) representing the statistical certainty
      of the verification decision relative to the configured threshold boundary.
    ---

    Mapping formulation:
    - At similarity == threshold, baseline neutral confidence is 0.50 (50%).
    - For scores > threshold, confidence scales from 0.50 to 0.99 as similarity approaches 1.0.
    - For scores < threshold, confidence scales below 0.50 down to 0.00 as similarity drops.

    Args:
        similarity_score: Cosine similarity value in [-1.0, 1.0].
        threshold: Configured verification decision threshold (e.g. 0.70).

    Returns:
        float: Calibrated confidence float value bounded in [0.0, 1.0].
    """
    if similarity_score >= threshold:
        # Distance to perfect match (1.0)
        margin_range = max(1e-6, 1.0 - threshold)
        excess = similarity_score - threshold
        confidence = 0.50 + 0.50 * (excess / margin_range)
    else:
        # Distance to minimum score threshold
        margin_range = max(1e-6, threshold - (-1.0))
        deficit = threshold - similarity_score
        confidence = 0.50 - 0.50 * (deficit / margin_range)

    return float(np.clip(round(confidence, 4), 0.0, 1.0))
