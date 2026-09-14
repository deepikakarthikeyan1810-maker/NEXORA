"""
Unit tests for ConversationAnalyzer in Nexora Risk Engine.
Tests contextual behavior detection, false positive suppression, and score calculation.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to sys.path to enable imports from risk-analysis root
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_analyzer import ConversationAnalyzer


@pytest.fixture
def analyzer():
    return ConversationAnalyzer()


def test_otp_request_detection(analyzer):
    """Test direct OTP request detection."""
    transcript = "Tell me your OTP immediately to verify your identity."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "OTP request" in factor_names
    assert score >= 35


def test_money_transfer_detection(analyzer):
    """Test financial money transfer detection."""
    transcript = "Please transfer ₹20,000 to this account right now."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Money transfer request" in factor_names
    assert score >= 35


def test_impersonation_detection_bank(analyzer):
    """Test bank impersonation detection."""
    transcript = "Hello, I am calling from your bank security team."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Possible bank impersonation" in factor_names


def test_impersonation_detection_police_govt(analyzer):
    """Test police and government official impersonation."""
    transcript = "I am speaking from the police station regarding an urgent cyber crime case."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Police / Government impersonation" in factor_names


def test_urgency_detection(analyzer):
    """Test unusual urgency pressure detection."""
    transcript = "You must take action right now within 5 minutes."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Unusual urgency / pressure" in factor_names


def test_threat_detection_account_blocking(analyzer):
    """Test account blocking threat detection."""
    transcript = "If you do not comply, your account will be blocked today."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Account blocking threat" in factor_names


def test_remote_access_detection(analyzer):
    """Test remote access tool request detection."""
    transcript = "Please install AnyDesk and give me remote access to assist you."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Remote access request" in factor_names
    assert "Software installation request" in factor_names


def test_sensitive_info_and_password_request(analyzer):
    """Test password and PIN request detection."""
    transcript = "Enter your secret ATM PIN and tell me your password."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Password / PIN request" in factor_names


def test_contextual_false_positive_handling(analyzer):
    """
    CRITICAL TEST: Ensure user statements referencing rules/warnings do NOT trigger alarms.
    'The bank told me never to share my OTP' should NOT trigger 'OTP request'.
    """
    transcript = "The bank told me never to share my OTP with anyone over the phone."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "OTP request" not in factor_names
    assert score == 0


def test_deduplication_and_multiple_factors(analyzer):
    """Ensure repeated phrases in same transcript don't double count identical factors."""
    transcript = (
        "I am calling from your bank. Your account will be blocked. "
        "Tell me your OTP. Again, give me the OTP right now!"
    )
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    
    # Check OTP request appears exactly once in factors
    otp_count = factor_names.count("OTP request")
    assert otp_count == 1
    assert "Possible bank impersonation" in factor_names
    assert "Account blocking threat" in factor_names


def test_empty_transcript(analyzer):
    """Test graceful handling of empty or blank transcript."""
    factors, score = analyzer.analyze("")
    assert factors == []
    assert score == 0


def test_compound_financial_social_engineering(analyzer):
    """Test compound pattern 1: Bank impersonation + OTP/credential + Money transfer."""
    transcript = "I am calling from your bank. Tell me your OTP and transfer ₹20,000 immediately."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Coordinated financial social-engineering pattern" in factor_names


def test_compound_remote_access_scam(analyzer):
    """Test compound pattern 2: Tech support impersonation + Remote access / software install."""
    transcript = "I'm from technical support. Install AnyDesk and give me remote access to your computer."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Coordinated remote-access scam pattern" in factor_names


def test_compound_coercive_impersonation(analyzer):
    """Test compound pattern 3: Police/Govt/Bank impersonation + Threat + Urgency."""
    transcript = "Calling from police station. Arrest warrant issued against you. Pay the fee right now."
    factors, score = analyzer.analyze(transcript)
    factor_names = [f.factor for f in factors]
    assert "Coercive impersonation pattern" in factor_names

