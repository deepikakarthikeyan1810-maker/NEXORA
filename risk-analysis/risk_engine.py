"""
Risk Engine for Nexora.
Orchestrates multi-modal risk scoring combining conversation behavior analysis,
voice anti-spoofing results, and speaker verification results.
"""

from typing import Dict, Any, List
from config import OVERALL_RISK_WEIGHTS, RISK_LEVEL_THRESHOLDS, RECOMMENDED_ACTIONS
from conversation_analyzer import ConversationAnalyzer
from models import AnalysisRequest, AnalysisResponse, RiskFactorItem


class RiskEngine:
    """
    Main Risk Scoring Engine.
    Combines Voice Authenticity Risk (Member 2), Speaker Verification Risk (Member 3),
    and Conversation Behavior Risk (Member 4) into a unified risk assessment.
    """

    def __init__(self):
        self.analyzer = ConversationAnalyzer()

    def evaluate(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Evaluates call payload and returns a comprehensive AnalysisResponse.
        """
        # 1. Analyze Conversation Transcript
        risk_factors, raw_conv_score = self.analyzer.analyze(request.transcript)
        conversation_risk_score = min(100, raw_conv_score)

        # 2. Convert Voice AI confidence scores to Risk Percentages (0.0 - 100.0)
        # voice_authenticity_score: 1.0 = genuine, 0.0 = spoofed clone
        # voice_risk: 0.0 = low risk (genuine), 100.0 = high risk (cloned)
        voice_auth = request.voice_authenticity_score if request.voice_authenticity_score is not None else 1.0
        voice_risk = round((1.0 - max(0.0, min(1.0, voice_auth))) * 100.0, 1)

        # speaker_verification_score: 1.0 = verified victim identity, 0.0 = unverified imposter
        # speaker_risk: 0.0 = low risk (verified), 100.0 = high risk (imposter)
        speaker_verif = request.speaker_verification_score if request.speaker_verification_score is not None else 1.0
        speaker_risk = round((1.0 - max(0.0, min(1.0, speaker_verif))) * 100.0, 1)

        # 3. Calculate Overall Multi-Modal Weighted Risk Score
        w_voice = OVERALL_RISK_WEIGHTS["voice_authenticity"]
        w_speaker = OVERALL_RISK_WEIGHTS["speaker_verification"]
        w_conv = OVERALL_RISK_WEIGHTS["conversation_behaviour"]

        calculated_score = (w_voice * voice_risk) + (w_speaker * speaker_risk) + (w_conv * conversation_risk_score)
        overall_risk_score = int(round(max(0.0, min(100.0, calculated_score))))

        # 4. Classify Risk Level
        risk_level = self._classify_risk_level(overall_risk_score)

        # 5. Determine Recommended Action
        recommended_action = RECOMMENDED_ACTIONS.get(risk_level, "ALLOW_CALL")

        # 6. Generate Human-Readable Explanation
        explanation = self._generate_explanation(
            overall_score=overall_risk_score,
            risk_level=risk_level,
            conv_score=conversation_risk_score,
            voice_risk=voice_risk,
            speaker_risk=speaker_risk,
            risk_factors=risk_factors
        )

        return AnalysisResponse(
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            conversation_risk_score=conversation_risk_score,
            voice_risk=voice_risk,
            speaker_risk=speaker_risk,
            risk_factors=risk_factors,
            explanation=explanation,
            recommended_action=recommended_action
        )

    def _classify_risk_level(self, score: int) -> str:
        """Maps numeric score (0-100) to risk level string (LOW, MEDIUM, HIGH)."""
        for level, (low, high) in RISK_LEVEL_THRESHOLDS.items():
            if low <= score <= high:
                return level
        return "HIGH" if score > 70 else "LOW"

    def _generate_explanation(
        self,
        overall_score: int,
        risk_level: str,
        conv_score: int,
        voice_risk: float,
        speaker_risk: float,
        risk_factors: List[RiskFactorItem]
    ) -> str:
        """
        Synthesizes a clear, operator-readable explanation detailing why the call is risky.
        """
        reasons = []

        # Conversation behaviors
        if risk_factors:
            factor_names = [f.factor for f in risk_factors]
            if len(factor_names) == 1:
                reasons.append(f"{factor_names[0]} detected in conversation")
            else:
                reasons.append(f"Multiple suspicious behaviors detected ({', '.join(factor_names)})")
        else:
            reasons.append("No suspicious conversational phrasing detected")

        # Voice spoofing signal
        if voice_risk >= 50.0:
            reasons.append(f"High synthetic voice clone probability (Voice Risk: {voice_risk:.0f}%)")
        elif voice_risk >= 25.0:
            reasons.append(f"Moderate voice authenticity anomaly (Voice Risk: {voice_risk:.0f}%)")

        # Speaker verification signal
        if speaker_risk >= 50.0:
            reasons.append(f"Speaker identity verification failed (Speaker Risk: {speaker_risk:.0f}%)")
        elif speaker_risk >= 25.0:
            reasons.append(f"Uncertain speaker verification match (Speaker Risk: {speaker_risk:.0f}%)")

        # Construct final text
        if risk_level == "HIGH":
            prefix = f"HIGH RISK ({overall_score}/100) — Impersonation attack likely."
        elif risk_level == "MEDIUM":
            prefix = f"MEDIUM RISK ({overall_score}/100) — Suspicious call requiring verification."
        else:
            prefix = f"LOW RISK ({overall_score}/100) — Call appears normal."

        return f"{prefix} Reasons: {'; '.join(reasons)}."
