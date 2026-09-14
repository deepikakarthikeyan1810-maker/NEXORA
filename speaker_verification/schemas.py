from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class EnrollmentResponse(BaseModel):
    """API Response model for speaker enrollment."""
    speaker_id: str = Field(..., description="Unique speaker identifier")
    status: str = Field(default="enrolled", description="Enrollment operation status")
    message: str = Field(..., description="Human readable result message")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of enrollment"
    )


class VerificationResponse(BaseModel):
    """
    API Response model for speaker verification.
    Meets Requirement 2 & 11.
    """
    speaker_id: str = Field(..., description="Target speaker identifier")
    verified: bool = Field(..., description="Boolean flag indicating whether speaker identity matches enrolled template")
    similarity_score: float = Field(..., description="Cosine similarity score between enrolled and incoming embeddings [-1.0, 1.0]")
    threshold: float = Field(..., description="Configured decision boundary threshold")
    confidence: float = Field(..., description="Calibrated confidence score [0.0, 1.0]")
    model: str = Field(default="ECAPA-TDNN", description="Model architecture used for embedding extraction")


class RiskEngineSignal(BaseModel):
    """
    Machine-readable signal payload for Nexora Risk Decision Engine.
    Meets Requirement 10.
    """
    signal: str = Field(default="speaker_verification", description="Signal classifier type identifier")
    speaker_verified: bool = Field(..., description="Identity match result")
    similarity_score: float = Field(..., description="Raw cosine similarity score")
    confidence: float = Field(..., description="Confidence level derived from similarity vs threshold")


class SpeakerStatusResponse(BaseModel):
    """API Response model for speaker enrollment status check."""
    speaker_id: str = Field(..., description="Speaker identifier")
    enrolled: bool = Field(..., description="Whether speaker embedding exists in database")


class ErrorDetail(BaseModel):
    """Standardized error payload representation."""
    error_code: str = Field(..., description="Unique domain error code string")
    message: str = Field(..., description="User friendly error explanation")
    speaker_id: Optional[str] = Field(default=None, description="Related speaker ID if applicable")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Error timestamp"
    )
