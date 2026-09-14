"""
Pydantic Data Models for Nexora Risk Analysis API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RiskFactorItem(BaseModel):
    """Represents an individual detected risk factor with evidence and severity."""
    factor: str = Field(..., description="Name of the detected risk factor")
    severity: str = Field(..., description="Severity level: HIGH, MEDIUM-HIGH, MEDIUM, LOW")
    evidence: str = Field(..., description="Transcript excerpt triggering this factor")
    score: int = Field(..., description="Score contribution to raw conversation risk")


class AnalysisRequest(BaseModel):
    """Input payload for POST /analyze endpoint."""
    transcript: str = Field(
        ...,
        description="Speech-to-text transcript of the call",
        json_schema_extra={"example": "I'm calling from your bank. Your account will be blocked. Give me the OTP and transfer ₹20,000 immediately."}
    )
    voice_authenticity_score: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Voice spoof detection score from Member 2 (1.0 = genuine voice, 0.0 = fake clone)"
    )
    speaker_verification_score: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="ECAPA-TDNN speaker verification score from Member 3 (1.0 = verified speaker, 0.0 = imposter)"
    )


class AnalysisResponse(BaseModel):
    """Output response payload from POST /analyze endpoint."""
    overall_risk_score: int = Field(..., ge=0, le=100, description="Final combined risk score (0-100)")
    risk_level: str = Field(..., description="Overall risk classification: LOW, MEDIUM, HIGH")
    conversation_risk_score: int = Field(..., ge=0, le=100, description="Normalized transcript risk score (0-100)")
    voice_risk: float = Field(..., ge=0.0, le=100.0, description="Calculated voice authenticity risk percentage")
    speaker_risk: float = Field(..., ge=0.0, le=100.0, description="Calculated speaker verification risk percentage")
    risk_factors: List[RiskFactorItem] = Field(default_factory=list, description="List of detected conversation risk factors")
    explanation: str = Field(..., description="Human-readable summary of risk factors and reasoning")
    recommended_action: str = Field(..., description="System recommendation: ALLOW_CALL, VERIFY_IDENTITY, CHALLENGE_OR_BLOCK")
