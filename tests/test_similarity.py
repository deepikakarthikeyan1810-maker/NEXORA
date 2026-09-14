import numpy as np
import pytest

from speaker_verification.similarity import (
    normalize_embedding,
    cosine_similarity,
    calculate_confidence,
)


def test_normalize_embedding():
    """Test L2 normalization of vectors."""
    vec = np.array([3.0, 4.0], dtype=np.float32)
    norm_vec = normalize_embedding(vec)
    assert np.isclose(np.linalg.norm(norm_vec), 1.0)
    assert np.allclose(norm_vec, [0.6, 0.8])


def test_identical_vectors_cosine_similarity():
    """Test that identical vectors yield cosine similarity 1.0."""
    vec = np.random.randn(192).astype(np.float32)
    sim = cosine_similarity(vec, vec)
    assert pytest.approx(sim, abs=1e-5) == 1.0


def test_orthogonal_vectors_cosine_similarity():
    """Test orthogonal vectors yield similarity 0.0."""
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    sim = cosine_similarity(v1, v2)
    assert pytest.approx(sim, abs=1e-5) == 0.0


def test_opposite_vectors_cosine_similarity():
    """Test anti-parallel vectors yield similarity -1.0."""
    v1 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    v2 = np.array([-1.0, -2.0, -3.0], dtype=np.float32)
    sim = cosine_similarity(v1, v2)
    assert pytest.approx(sim, abs=1e-5) == -1.0


def test_confidence_calculation_at_threshold():
    """Test confidence is exactly 0.50 when similarity equals threshold."""
    thresh = 0.70
    conf = calculate_confidence(similarity_score=0.70, threshold=thresh)
    assert conf == 0.50


def test_confidence_calculation_above_threshold():
    """Test confidence scales above 0.50 for high similarity scores."""
    thresh = 0.70
    conf_mid = calculate_confidence(similarity_score=0.85, threshold=thresh)
    conf_high = calculate_confidence(similarity_score=1.00, threshold=thresh)
    
    assert conf_mid > 0.50
    assert conf_high == 1.00
    assert conf_high > conf_mid


def test_confidence_calculation_below_threshold():
    """Test confidence drops below 0.50 for low similarity scores."""
    thresh = 0.70
    conf_low = calculate_confidence(similarity_score=0.40, threshold=thresh)
    conf_zero = calculate_confidence(similarity_score=-1.0, threshold=thresh)

    assert conf_low < 0.50
    assert conf_zero == 0.00
