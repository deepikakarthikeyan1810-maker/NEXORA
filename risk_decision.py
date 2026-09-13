from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskDecision:
    risk_score: float
    risk_level: str
    confidence: float
    primary_risks: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    recommended_action: str = "MONITOR"


class RiskDecisionEngine:
    """Converts compound risk analysis into an actionable decision."""

    THRESHOLDS = {
        "LOW": 0,
        "MEDIUM": 30,
        "HIGH": 60,
        "CRITICAL": 80,
    }

    def decide(
        self,
        risk_score: float,
        primary_risks: List[str] | None = None,
        evidence: List[str] | None = None,
        confidence: float = 0.0,
    ) -> RiskDecision:

        risk_score = max(0.0, min(100.0, risk_score))
        confidence = max(0.0, min(1.0, confidence))

        if risk_score >= self.THRESHOLDS["CRITICAL"]:
            risk_level = "CRITICAL"
            action = "ESCALATE"
        elif risk_score >= self.THRESHOLDS["HIGH"]:
            risk_level = "HIGH"
            action = "ESCALATE"
        elif risk_score >= self.THRESHOLDS["MEDIUM"]:
            risk_level = "MEDIUM"
            action = "MONITOR"
        else:
            risk_level = "LOW"
            action = "MONITOR"

        return RiskDecision(
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            confidence=round(confidence, 2),
            primary_risks=primary_risks or [],
            evidence=evidence or [],
            recommended_action=action,
        )
