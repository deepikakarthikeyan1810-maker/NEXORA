"""
Conversation & Behavior Analysis Engine for Nexora.
Analyzes speech-to-text live transcripts using contextual rule-based NLP.
Detects social engineering, impersonation, credential theft, and coercion patterns.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from config import FACTOR_CONFIGS
from models import RiskFactorItem


# Contextual suppressors / Negation patterns indicating warning, rule state, or refusal
# e.g., "The bank told me never to share my OTP" or "I will not share my password"
FALSE_POSITIVE_SUPPRESSORS = [
    r"\bnever\s+share\b",
    r"\btold\s+me\s+(?:not|never)\s+to\b",
    r"\bdon'?t\s+share\b",
    r"\bwill\s+not\s+give\b",
    r"\bwon'?t\s+share\b",
    r"\bshould\s+not\s+share\b",
    r"\bdo\s+not\s+give\b",
    r"\bdo\s+not\s+share\b",
    r"\bwarning\s+about\b",
    r"\baware\s+of\s+scams\b",
    r"\bnever\s+give\b"
]


class ConversationAnalyzer:
    """
    Contextual Rule-Based Analyzer for live call transcripts.
    Identifies specific risk behaviors without simple naive keyword flagging.
    """

    def __init__(self):
        self.configs = FACTOR_CONFIGS

    def split_into_sentences(self, text: str) -> List[str]:
        """Splits transcript into sentences/clauses for precise context and evidence extraction."""
        raw_sentences = re.split(r'[.!?;\n]+', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        return sentences if sentences else [text.strip()]

    def is_suppressed(self, sentence: str) -> bool:
        """
        Checks if a sentence contains context indicating a refusal, user rule reference,
        or awareness statement rather than a scammer request.
        """
        sent_lower = sentence.lower()
        for pattern in FALSE_POSITIVE_SUPPRESSORS:
            if re.search(pattern, sent_lower):
                return True
        return False

    def analyze(self, transcript: str) -> Tuple[List[RiskFactorItem], int]:
        """
        Analyzes the call transcript for suspicious behaviors.
        Returns a tuple of (list of detected RiskFactorItems, raw_score).
        """
        if not transcript or not transcript.strip():
            return [], 0

        sentences = self.split_into_sentences(transcript)
        full_transcript_lower = transcript.lower()

        detected_factors: List[RiskFactorItem] = []
        detected_categories = set()

        # 1. OTP Request Detection
        if "otp_request" not in detected_categories:
            otp_match = self._detect_otp_request(sentences)
            if otp_match:
                detected_categories.add("otp_request")
                detected_factors.append(self._build_factor("otp_request", otp_match))

        # 2. Money / Financial Transfer Request Detection
        if "financial_transfer" not in detected_categories:
            match = self._detect_financial_transfer(sentences)
            if match:
                detected_categories.add("financial_transfer")
                detected_factors.append(self._build_factor("financial_transfer", match))

        # 3. Password / PIN Request Detection
        if "password_pin_request" not in detected_categories:
            match = self._detect_password_pin_request(sentences)
            if match:
                detected_categories.add("password_pin_request")
                detected_factors.append(self._build_factor("password_pin_request", match))

        # 4. Bank / Account Credential Request
        if "bank_credential_request" not in detected_categories:
            match = self._detect_bank_credentials(sentences)
            if match:
                detected_categories.add("bank_credential_request")
                detected_factors.append(self._build_factor("bank_credential_request", match))

        # 5. Card Information Request
        if "card_info_request" not in detected_categories:
            match = self._detect_card_info_request(sentences)
            if match:
                detected_categories.add("card_info_request")
                detected_factors.append(self._build_factor("card_info_request", match))

        # 6. Remote Access Request
        if "remote_access_request" not in detected_categories:
            match = self._detect_remote_access(sentences)
            if match:
                detected_categories.add("remote_access_request")
                detected_factors.append(self._build_factor("remote_access_request", match))

        # 7. Software Installation Request
        if "software_install_request" not in detected_categories:
            match = self._detect_software_install(sentences)
            if match:
                detected_categories.add("software_install_request")
                detected_factors.append(self._build_factor("software_install_request", match))

        # 8. Bank Impersonation
        if "bank_impersonation" not in detected_categories:
            match = self._detect_bank_impersonation(sentences)
            if match:
                detected_categories.add("bank_impersonation")
                detected_factors.append(self._build_factor("bank_impersonation", match))

        # 9. Police / Government Impersonation
        if "govt_police_impersonation" not in detected_categories:
            match = self._detect_govt_police_impersonation(sentences)
            if match:
                detected_categories.add("govt_police_impersonation")
                detected_factors.append(self._build_factor("govt_police_impersonation", match))

        # 10. Tech Support Impersonation
        if "tech_support_impersonation" not in detected_categories:
            match = self._detect_tech_support_impersonation(sentences)
            if match:
                detected_categories.add("tech_support_impersonation")
                detected_factors.append(self._build_factor("tech_support_impersonation", match))

        # 11. Account Blocking Threat
        if "account_blocking_threat" not in detected_categories:
            match = self._detect_account_blocking_threat(sentences)
            if match:
                detected_categories.add("account_blocking_threat")
                detected_factors.append(self._build_factor("account_blocking_threat", match))

        # 12. Fear / Threat Language
        if "fear_threat_language" not in detected_categories:
            match = self._detect_fear_threat_language(sentences)
            if match:
                detected_categories.add("fear_threat_language")
                detected_factors.append(self._build_factor("fear_threat_language", match))

        # 13. Unusual Urgency / Pressure
        if "unusual_urgency" not in detected_categories:
            match = self._detect_unusual_urgency(sentences)
            if match:
                detected_categories.add("unusual_urgency")
                detected_factors.append(self._build_factor("unusual_urgency", match))

        # 14. Suspicious Link
        if "suspicious_link" not in detected_categories:
            match = self._detect_suspicious_link(sentences)
            if match:
                detected_categories.add("suspicious_link")
                detected_factors.append(self._build_factor("suspicious_link", match))

        # 15. Bypass Verification Attempt
        if "bypass_verification" not in detected_categories:
            match = self._detect_bypass_verification(sentences)
            if match:
                detected_categories.add("bypass_verification")
                detected_factors.append(self._build_factor("bypass_verification", match))

        # 16. Secrecy Request
        if "secrecy_request" not in detected_categories:
            match = self._detect_secrecy_request(sentences)
            if match:
                detected_categories.add("secrecy_request")
                detected_factors.append(self._build_factor("secrecy_request", match))

        # 17. Confidential Information Request
        if "confidential_info_request" not in detected_categories:
            match = self._detect_confidential_info(sentences)
            if match:
                detected_categories.add("confidential_info_request")
                detected_factors.append(self._build_factor("confidential_info_request", match))

        # 18. Urgent Payment Request
        if "urgent_payment" not in detected_categories:
            match = self._detect_urgent_payment(sentences)
            if match:
                detected_categories.add("urgent_payment")
                detected_factors.append(self._build_factor("urgent_payment", match))

        # Second-Stage Compound Risk Analysis Layer
        compound = self._detect_compound_risk(detected_categories)
        if compound:
            detected_factors.append(compound)

        raw_score = sum(f.score for f in detected_factors)
        return detected_factors, raw_score

    def _detect_compound_risk(self, detected_categories: set) -> Optional[RiskFactorItem]:
        """
        Evaluates second-stage compound risk patterns from first-stage detected categories.
        Returns at most ONE RiskFactorItem if a compound pattern matches, or None.
        """
        # 1. Coordinated financial social-engineering pattern
        if "bank_impersonation" in detected_categories:
            if detected_categories.intersection({"otp_request", "bank_credential_request", "card_info_request", "password_pin_request"}):
                if detected_categories.intersection({"financial_transfer", "urgent_payment"}):
                    return RiskFactorItem(
                        factor="Coordinated financial social-engineering pattern",
                        severity="HIGH",
                        evidence="Bank impersonation combined with credential collection and financial action request",
                        score=25
                    )

        # 2. Coordinated remote-access scam pattern
        if "tech_support_impersonation" in detected_categories:
            if detected_categories.intersection({"remote_access_request", "software_install_request"}):
                return RiskFactorItem(
                    factor="Coordinated remote-access scam pattern",
                    severity="HIGH",
                    evidence="Technical support impersonation combined with remote access or software installation request",
                    score=25
                )

        # 3. Coercive impersonation pattern
        if detected_categories.intersection({"bank_impersonation", "govt_police_impersonation", "tech_support_impersonation"}):
            if detected_categories.intersection({"account_blocking_threat", "fear_threat_language"}):
                if detected_categories.intersection({"unusual_urgency", "urgent_payment"}):
                    return RiskFactorItem(
                        factor="Coercive impersonation pattern",
                        severity="HIGH",
                        evidence="Impersonation combined with threat language and immediate pressure",
                        score=20
                    )

        # 4. Coordinated social-engineering pattern
        if detected_categories.intersection({"bank_impersonation", "govt_police_impersonation", "tech_support_impersonation"}):
            if detected_categories.intersection({"otp_request", "bank_credential_request", "card_info_request", "password_pin_request", "confidential_info_request"}):
                if detected_categories.intersection({"unusual_urgency", "secrecy_request", "bypass_verification"}):
                    return RiskFactorItem(
                        factor="Coordinated social-engineering pattern",
                        severity="HIGH",
                        evidence="Impersonation combined with sensitive information request and manipulation tactics",
                        score=20
                    )

        return None

    def _build_factor(self, key: str, evidence: str) -> RiskFactorItem:
        cfg = self.configs[key]
        return RiskFactorItem(
            factor=cfg["factor"],
            severity=cfg["severity"],
            evidence=evidence,
            score=cfg["score"]
        )

    # -------------------------------------------------------------------------
    # Category-Specific Detection Logic
    # -------------------------------------------------------------------------

    def _detect_otp_request(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:tell|give|share|send|provide|read|enter)\s+(?:me\s+)?(?:your\s+|the\s+)?(?:otp|one\s+time\s+passcode|verification\s+code|code)\b",
            r"\bwhat\s+is\s+(?:your\s+|the\s+)?(?:otp|code|passcode)\b",
            r"\botp\s+(?:sent|received)\b.*\b(?:tell|give|share)\b",
            r"\bshare\s+the\s+code\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_financial_transfer(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:transfer|send|wire|pay)\s+(?:me\s+)?(?:the\s+)?(?:money|funds|rs\.?|inr|rupees|\$?[\d,]+)\b",
            r"\btransfer\s+(?:₹|rs\.?|inr)?\s*[\d,]+\b",
            r"\bmake\s+(?:a\s+)?payment\b",
            r"\bsend\s+money\s+immediately\b",
            r"\btransfer\s+immediately\b",
            r"\bpay\s+the\s+amount\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_password_pin_request(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:tell|give|share|provide|enter)\s+(?:me\s+)?(?:your\s+)?(?:password|pin|atm\s+pin|login\s+passcode|secret\s+code)\b",
            r"\bwhat\s+is\s+your\s+(?:password|pin)\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_bank_credentials(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:tell|give|share|verify|send|provide)\s+(?:me\s+)?(?:your\s+)?(?:account\s+details|account\s+number|bank\s+details|netbanking|cvv)\b",
            r"\baccount\s+details\b.*\b(?:verify|send|give|share)\b",
            r"\b(?:send|give|share)\b.*\baccount\s+details\b",
            r"\bverify\s+your\s+(?:account|banking)\s+details\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_card_info_request(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:credit|debit)\s+card\s+(?:number|details|cvv|expiry)\b",
            r"\bshare\s+your\s+card\s+details\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_remote_access(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:anydesk|teamviewer|quicksupport|remote\s+access|screen\s+share)\b",
            r"\bgive\s+(?:me\s+)?remote\s+access\b",
            r"\bshare\s+your\s+screen\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_software_install(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:install|download|run|execute)\s+(?:this\s+)?(?:application|app|apk|software|tool|file|anydesk|teamviewer|quicksupport)\b",
            r"\bdownload\s+this\s+application\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_bank_impersonation(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:calling|speaking)\s+from\s+(?:your\s+)?(?:bank|sbi|hdfc|icici|axis|rbi|fraud\s+department|security\s+team)\b",
            r"\bi'?m\s+from\s+(?:the\s+)?bank\b",
            r"\bbank\s+verification\s+team\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_govt_police_impersonation(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:calling|speaking)\s+from\s+(?:the\s+)?(?:police|cbi|income\s+tax|government|cyber\s+cell|trai|court)\b",
            r"\bi'?m\s+(?:a\s+)?police\s+officer\b",
            r"\bcustoms\s+department\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_tech_support_impersonation(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:calling|speaking)\s+from\s+(?:technical|tech|customer)\s+support\b",
            r"\bi'?m\s+from\s+technical\s+support\b",
            r"\bhelpdesk\s+engineer\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_account_blocking_threat(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\baccount\s+will\s+be\s+(?:blocked|suspended|deactivated|frozen|terminated)\b",
            r"\bcard\s+will\s+be\s+blocked\b",
            r"\bblock\s+your\s+account\b",
            r"\baccount\s+blockage\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_fear_threat_language(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:arrest\s+warrant|legal\s+action|police\s+case|court\s+notice|penalty|fine)\b",
            r"\bface\s+legal\s+consequences\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_unusual_urgency(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:immediately|right\s+now|within\s+\d+\s+minutes|urgent|urgently|no\s+time)\b",
            r"\bdo\s+it\s+fast\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_suspicious_link(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:click|open)\s+(?:the|this)\s+(?:link|url|website)\b",
            r"\bbit\.ly|\bgoo\.gl|\bshorturl\b",
            r"\blink\s+sent\s+to\s+your\s+phone\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_bypass_verification(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\bdon'?t\s+go\s+to\s+(?:the\s+)?(?:bank|branch)\b",
            r"\bdo\s+not\s+call\s+(?:customer\s+care|official\s+number)\b",
            r"\bbypass\s+verification\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_secrecy_request(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:don'?t|do\s+not)\s+tell\s+(?:anyone|your\s+family|bank)\b",
            r"\bkeep\s+this\s+(?:secret|confidential)\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_confidential_info(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\b(?:share|tell|give)\s+(?:me\s+)?(?:confidential|sensitive)\s+(?:info|information|data)\b",
            r"\bpersonal\s+identity\s+details\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None

    def _detect_urgent_payment(self, sentences: List[str]) -> Optional[str]:
        patterns = [
            r"\burgent\s+payment\b",
            r"\bpay\s+the\s+fee\s+now\b"
        ]
        for sentence in sentences:
            if self.is_suppressed(sentence):
                continue
            s_lower = sentence.lower()
            for pat in patterns:
                if re.search(pat, s_lower):
                    return sentence
        return None
