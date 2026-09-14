"""
Unit and Integration tests for RiskEngine and FastAPI routes in Nexora.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from risk_engine import RiskEngine
from models import AnalysisRequest
from app import app


@pytest.fixture
def engine():
    return RiskEngine()


@pytest.fixture
def client():
    return TestClient(app)


def test_scenario_1_normal_call(engine):
    """SCENARIO 1 — NORMAL: 'Hey, are we still meeting at 5 today?' -> Expected LOW (ALLOW_CALL)"""
    request = AnalysisRequest(
        transcript="Hey, are we still meeting at 5 today?",
        voice_authenticity_score=0.95,
        speaker_verification_score=0.90
    )
    response = engine.evaluate(request)
    assert response.risk_level == "LOW"
    assert response.recommended_action == "ALLOW_CALL"
    assert response.overall_risk_score < 40


def test_scenario_2_suspicious_call(engine):
    """SCENARIO 2 — SUSPICIOUS: Vague account details request -> Expected MEDIUM (VERIFY_IDENTITY)"""
    request = AnalysisRequest(
        transcript="Can you send me your account details? I need to verify something.",
        voice_authenticity_score=0.50,
        speaker_verification_score=0.50
    )
    response = engine.evaluate(request)
    assert response.risk_level == "MEDIUM"
    assert response.recommended_action == "VERIFY_IDENTITY"
    assert 40 <= response.overall_risk_score <= 69


def test_scenario_3_high_risk_impersonation(engine):
    """SCENARIO 3 — HIGH RISK IMPERSONATION: Bank impersonation + OTP + Money transfer -> Expected HIGH (CHALLENGE_OR_BLOCK)"""
    request = AnalysisRequest(
        transcript="I'm calling from your bank. Your account will be blocked. Tell me your OTP and transfer ₹20,000 immediately.",
        voice_authenticity_score=0.35,
        speaker_verification_score=0.40
    )
    response = engine.evaluate(request)
    assert response.risk_level == "HIGH"
    assert response.recommended_action == "CHALLENGE_OR_BLOCK"
    assert response.overall_risk_score >= 70


def test_scenario_4_remote_access_attack(engine):
    """SCENARIO 4 — REMOTE ACCESS: Tech support impersonation + AnyDesk/Remote access -> Expected HIGH"""
    request = AnalysisRequest(
        transcript="I'm from technical support. Install this application and give me remote access to your computer.",
        voice_authenticity_score=0.30,
        speaker_verification_score=0.25
    )
    response = engine.evaluate(request)
    assert response.risk_level == "HIGH"
    assert response.recommended_action == "CHALLENGE_OR_BLOCK"
    assert response.overall_risk_score >= 70


def test_scenario_5_contextual_otp_statement(engine):
    """SCENARIO 5 — CONTEXTUAL OTP: 'The bank told me never to share my OTP' -> Expected LOW"""
    request = AnalysisRequest(
        transcript="The bank told me never to share my OTP with anyone over the phone.",
        voice_authenticity_score=0.95,
        speaker_verification_score=0.92
    )
    response = engine.evaluate(request)
    assert response.risk_level == "LOW"
    assert response.recommended_action == "ALLOW_CALL"
    assert response.conversation_risk_score == 0


def test_voice_risk_conversion(engine):
    """Test voice authenticity score conversion (1.0 = genuine voice -> 0% voice risk)."""
    request = AnalysisRequest(
        transcript="Hello, how are you?",
        voice_authenticity_score=0.20,  # 80% voice risk
        speaker_verification_score=1.0  # 0% speaker risk
    )
    response = engine.evaluate(request)
    assert response.voice_risk == 80.0
    assert response.speaker_risk == 0.0


def test_fastapi_analyze_endpoint(client):
    """Test POST /analyze API endpoint."""
    payload = {
        "transcript": "I'm calling from your bank. Tell me the OTP immediately.",
        "voice_authenticity_score": 0.35,
        "speaker_verification_score": 0.40
    }
    res = client.post("/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "overall_risk_score" in data
    assert "risk_level" in data
    assert "recommended_action" in data
    assert "risk_factors" in data
    assert "explanation" in data


def test_fastapi_health_endpoint(client):
    """Test GET /health API endpoint."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy", "service": "nexora-risk-analysis"}
