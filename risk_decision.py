"""
Structured risk decision and explainability layer for Nexora.

This module does not recalculate the risk score.
It consumes the already-computed Nexora RiskEngine outputs and
packages them into a structured decision object.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskDecision:
    """Structured, explainable risk decision."""

    risk_score: int
    risk_level: str
    confidence: float
    primary_risks: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    recommended_action: str = "ALLOW_CALL"


class RiskDecisionEngine:
    """
    Converts an existing Nexora risk assessment into a structured
    decision without changing the underlying scoring logic.
    """

    VALID_LEVELS = {"LOW", "MEDIUM", "HIGH"}

    VALID_ACTIONS = {
        "ALLOW_CALL",
        "VERIFY_IDENTITY",
        "CHALLENGE_OR_BLOCK",
    }

    def decide(
        self,
        risk_score: int,
        risk_level: str,
        recommended_action: str,
        primary_risks: List[str] | None = None,
        evidence: List[str] | None = None,
        confidence: float = 0.0,
    ) -> RiskDecision:
        """Build a structured decision from existing RiskEngine output."""

        risk_score = max(0, min(100, int(round(risk_score))))
        confidence = max(0.0, min(1.0, float(confidence)))

        if risk_level not in self.VALID_LEVELS:
            raise ValueError(
                f"Invalid risk level: {risk_level}. "
                f"Expected one of {sorted(self.VALID_LEVELS)}."
            )

        if recommended_action not in self.VALID_ACTIONS:
            raise ValueError(
                f"Invalid recommended action: {recommended_action}. "
                f"Expected one of {sorted(self.VALID_ACTIONS)}."
            )

        return RiskDecision(
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=round(confidence, 2),
            primary_risks=primary_risks or [],
            evidence=evidence or [],
            recommended_action=recommended_action,
        )
