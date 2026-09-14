"""
Config module for Nexora Risk Analysis Engine.
All risk scoring weights, severity levels, thresholds, and detection rules are defined here.
"""

from typing import Dict, Any

# Risk Level Thresholds (0-100)
RISK_LEVEL_THRESHOLDS = {
    "LOW": (0, 39),
    "MEDIUM": (40, 69),
    "HIGH": (70, 100)
}

# Response Actions based on Risk Level
RECOMMENDED_ACTIONS = {
    "LOW": "ALLOW_CALL",
    "MEDIUM": "VERIFY_IDENTITY",
    "HIGH": "CHALLENGE_OR_BLOCK"
}

# Multi-modal Overall Risk Weights (Must sum to 1.0)
# Prototype/Demo weights as specified in system requirements
OVERALL_RISK_WEIGHTS = {
    "voice_authenticity": 0.30,
    "speaker_verification": 0.30,
    "conversation_behaviour": 0.40
}

# Conversation Risk Categories, Severities, and Default Score Contributions
# Max conversation risk score is normalized to 100
FACTOR_CONFIGS: Dict[str, Dict[str, Any]] = {
    "otp_request": {
        "factor": "OTP request",
        "severity": "HIGH",
        "score": 35,
        "description": "Request for One-Time Password or authentication passcode."
    },
    "financial_transfer": {
        "factor": "Money transfer request",
        "severity": "HIGH",
        "score": 35,
        "description": "Direct request for wire transfer, UPI payment, or funds transfer."
    },
    "password_pin_request": {
        "factor": "Password / PIN request",
        "severity": "HIGH",
        "score": 35,
        "description": "Request for account login passwords, PINs, or security codes."
    },
    "bank_credential_request": {
        "factor": "Bank credential request",
        "severity": "HIGH",
        "score": 30,
        "description": "Request for bank account numbers, CVVs, or login credentials."
    },
    "card_info_request": {
        "factor": "Card information request",
        "severity": "HIGH",
        "score": 30,
        "description": "Request for credit or debit card numbers, expiry dates, or security details."
    },
    "remote_access_request": {
        "factor": "Remote access request",
        "severity": "HIGH",
        "score": 30,
        "description": "Request to gain remote desktop access or control of user's device."
    },
    "software_install_request": {
        "factor": "Software installation request",
        "severity": "HIGH",
        "score": 25,
        "description": "Instruction to install third-party apps, APKs, or executable files."
    },
    "bank_impersonation": {
        "factor": "Possible bank impersonation",
        "severity": "HIGH",
        "score": 25,
        "description": "Caller claiming to represent bank or financial institution."
    },
    "govt_police_impersonation": {
        "factor": "Police / Government impersonation",
        "severity": "HIGH",
        "score": 25,
        "description": "Caller claiming to represent police, CBI, tax authority, or government."
    },
    "tech_support_impersonation": {
        "factor": "Technical support impersonation",
        "severity": "HIGH",
        "score": 20,
        "description": "Caller claiming to be from customer care, IT support, or service desk."
    },
    "account_blocking_threat": {
        "factor": "Account blocking threat",
        "severity": "MEDIUM-HIGH",
        "score": 20,
        "description": "Threat of account suspension, card blockage, or immediate penalty."
    },
    "fear_threat_language": {
        "factor": "Fear / threat language",
        "severity": "MEDIUM-HIGH",
        "score": 20,
        "description": "Use of legal threats, arrest warnings, or intimidating language."
    },
    "unusual_urgency": {
        "factor": "Unusual urgency / pressure",
        "severity": "MEDIUM-HIGH",
        "score": 15,
        "description": "Pressuring victim to act immediately without verifying."
    },
    "suspicious_link": {
        "factor": "Suspicious link",
        "severity": "MEDIUM-HIGH",
        "score": 15,
        "description": "Directing victim to open external links, short URLs, or phishing sites."
    },
    "bypass_verification": {
        "factor": "Bypass verification attempt",
        "severity": "MEDIUM-HIGH",
        "score": 15,
        "description": "Instructing victim not to visit branch or check with official support."
    },
    "secrecy_request": {
        "factor": "Secrecy request",
        "severity": "MEDIUM-HIGH",
        "score": 15,
        "description": "Instructing victim to keep call secret from family, bank, or authorities."
    },
    "confidential_info_request": {
        "factor": "Confidential information request",
        "severity": "MEDIUM-HIGH",
        "score": 15,
        "description": "Asking for sensitive personal, identity, or security information."
    },
    "urgent_payment": {
        "factor": "Urgent payment request",
        "severity": "MEDIUM-HIGH",
        "score": 15,
        "description": "Demanding quick payment under pretext of emergency."
    }
}
