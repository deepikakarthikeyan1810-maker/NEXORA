import pytest

from risk_decision import RiskDecisionEngine


@pytest.fixture
def engine():
    return RiskDecisionEngine()


def test_low_risk_decision(engine):
    result = engine.decide(
        risk_score=25,
        risk_level="LOW",
        recommended_action="ALLOW_CALL",
    )

    assert result.risk_score == 25
    assert result.risk_level == "LOW"
    assert result.recommended_action == "ALLOW_CALL"


def test_medium_risk_decision(engine):
    result = engine.decide(
        risk_score=55,
        risk_level="MEDIUM",
        recommended_action="VERIFY_IDENTITY",
    )

    assert result.risk_score == 55
    assert result.risk_level == "MEDIUM"
    assert result.recommended_action == "VERIFY_IDENTITY"


def test_high_risk_decision(engine):
    result = engine.decide(
        risk_score=85,
        risk_level="HIGH",
        recommended_action="CHALLENGE_OR_BLOCK",
    )

    assert result.risk_score == 85
    assert result.risk_level == "HIGH"
    assert result.recommended_action == "CHALLENGE_OR_BLOCK"


def test_score_is_clamped(engine):
    result = engine.decide(
        risk_score=120,
        risk_level="HIGH",
        recommended_action="CHALLENGE_OR_BLOCK",
    )

    assert result.risk_score == 100


def test_negative_score_is_clamped(engine):
    result = engine.decide(
        risk_score=-10,
        risk_level="LOW",
        recommended_action="ALLOW_CALL",
    )

    assert result.risk_score == 0


def test_confidence_is_clamped(engine):
    result = engine.decide(
        risk_score=50,
        risk_level="MEDIUM",
        recommended_action="VERIFY_IDENTITY",
        confidence=1.5,
    )

    assert result.confidence == 1.0


def test_negative_confidence_is_clamped(engine):
    result = engine.decide(
        risk_score=50,
        risk_level="MEDIUM",
        recommended_action="VERIFY_IDENTITY",
        confidence=-0.5,
    )

    assert result.confidence == 0.0


def test_confidence_is_rounded(engine):
    result = engine.decide(
        risk_score=50,
        risk_level="MEDIUM",
        recommended_action="VERIFY_IDENTITY",
        confidence=0.876,
    )

    assert result.confidence == 0.88


def test_primary_risks_are_preserved(engine):
    risks = [
        "OTP request",
        "Possible bank impersonation",
        "Account blocking threat",
    ]

    result = engine.decide(
        risk_score=80,
        risk_level="HIGH",
        recommended_action="CHALLENGE_OR_BLOCK",
        primary_risks=risks,
    )

    assert result.primary_risks == risks


def test_evidence_is_preserved(engine):
    evidence = [
        "Caller requested OTP",
        "Caller demanded immediate transfer",
    ]

    result = engine.decide(
        risk_score=80,
        risk_level="HIGH",
        recommended_action="CHALLENGE_OR_BLOCK",
        evidence=evidence,
    )

    assert result.evidence == evidence


def test_invalid_risk_level_is_rejected(engine):
    with pytest.raises(ValueError):
        engine.decide(
            risk_score=50,
            risk_level="CRITICAL",
            recommended_action="VERIFY_IDENTITY",
        )


def test_invalid_action_is_rejected(engine):
    with pytest.raises(ValueError):
        engine.decide(
            risk_score=50,
            risk_level="MEDIUM",
            recommended_action="ESCALATE",
        )


def test_empty_risk_lists_are_safe(engine):
    result = engine.decide(
        risk_score=20,
        risk_level="LOW",
        recommended_action="ALLOW_CALL",
    )

    assert result.primary_risks == []
    assert result.evidence == []
