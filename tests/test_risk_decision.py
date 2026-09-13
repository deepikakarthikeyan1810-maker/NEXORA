import pytest

from risk_decision import RiskDecisionEngine


@pytest.fixture
def engine():
    return RiskDecisionEngine()


def test_low_risk(engine):
    result = engine.decide(20)

    assert result.risk_level == "LOW"
    assert result.recommended_action == "MONITOR"


def test_medium_risk(engine):
    result = engine.decide(45)

    assert result.risk_level == "MEDIUM"
    assert result.recommended_action == "MONITOR"


def test_high_risk(engine):
    result = engine.decide(70)

    assert result.risk_level == "HIGH"
    assert result.recommended_action == "ESCALATE"


def test_critical_risk(engine):
    result = engine.decide(90)

    assert result.risk_level == "CRITICAL"
    assert result.recommended_action == "ESCALATE"


def test_low_boundary(engine):
    result = engine.decide(29)

    assert result.risk_level == "LOW"


def test_medium_boundary(engine):
    result = engine.decide(30)

    assert result.risk_level == "MEDIUM"


def test_high_boundary(engine):
    result = engine.decide(60)

    assert result.risk_level == "HIGH"


def test_critical_boundary(engine):
    result = engine.decide(80)

    assert result.risk_level == "CRITICAL"


def test_score_clamped_below_zero(engine):
    result = engine.decide(-10)

    assert result.risk_score == 0
    assert result.risk_level == "LOW"


def test_score_clamped_above_hundred(engine):
    result = engine.decide(120)

    assert result.risk_score == 100
    assert result.risk_level == "CRITICAL"


def test_confidence_clamped_below_zero(engine):
    result = engine.decide(50, confidence=-0.5)

    assert result.confidence == 0


def test_confidence_clamped_above_one(engine):
    result = engine.decide(50, confidence=1.5)

    assert result.confidence == 1


def test_primary_risks_preserved(engine):
    risks = ["coercive_language", "threat_escalation"]

    result = engine.decide(
        75,
        primary_risks=risks,
    )

    assert result.primary_risks == risks


def test_evidence_preserved(engine):
    evidence = [
        "Repeated threatening language",
        "Escalating pressure",
    ]

    result = engine.decide(
        75,
        evidence=evidence,
    )

    assert result.evidence == evidence


def test_score_is_rounded(engine):
    result = engine.decide(72.5678)

    assert result.risk_score == 72.57


def test_confidence_is_rounded(engine):
    result = engine.decide(
        72,
        confidence=0.8765,
    )

    assert result.confidence == 0.88
