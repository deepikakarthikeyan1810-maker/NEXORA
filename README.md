# Nexora — Real-Time Risk Analysis Engine (Member 4 Module)

> **SIH Problem Statement**: SIH22104 – AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attack  
> **Project Name**: Nexora  
> **Module Owner**: Member 4 — Conversation & Risk Analysis + Risk-Based Scoring  

---

## 📌 Module Purpose & Overview

The **Conversation & Risk Analysis Engine** is the core decision-making module of the **Nexora** anti-impersonation platform. It performs two-stage real-time contextual NLP analysis on speech-to-text live call transcripts and fuses these behavioral signals with voice authenticity (Member 2) and speaker verification (Member 3) scores. 

The module answers seven critical questions in real-time during a call:
1. **What is the caller asking the victim to do?** (First-stage intent & behavior extraction)
2. **Is the conversation suspicious?** (Second-stage compound pattern matching & contextual scoring)
3. **What risk factors are present?** (Categorized evidence-backed threat list + compound attack vectors)
4. **How risky is the conversation?** (Normalized 0–100 conversation risk score)
5. **How does conversation risk combine with voice AI signals?** (Multi-modal weighted fusion)
6. **Why was the final risk score generated?** (Human-readable operator explanation)
7. **What action should the system recommend?** (`ALLOW_CALL`, `VERIFY_IDENTITY`, `CHALLENGE_OR_BLOCK`)

---

## 🏗️ System Architecture & Data Flow

```
                                      LIVE CALL
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 AUDIO STREAM                    SPEECH-TO-TEXT (STT)
                         │                               │
           ┌─────────────┴─────────────┐                 │
           ▼                           ▼                 ▼
   [Member 2 Module]           [Member 3 Module]     TRANSCRIPT
Voice Spoof Detection       ECAPA-TDNN Verification      │
 (voice_authenticity_score) (speaker_verification_score) │
           │                           │                 ▼
           └─────────────┬─────────────┘         SENTENCE SPLITTING
                         │                               │
                         │                               ▼
                         │                    18 FIRST-STAGE DETECTORS
                         │                               │
                         │                               ▼
                         │                    DETECTED CATEGORIES (SET)
                         │                               │
                         │                               ▼
                         │                   COMPOUND RISK ANALYSIS LAYER
                         │                               │
                         │                               ▼
                         │                   RAW CONVERSATION SCORE (0-100)
                         │                               │
                         └───────────────┬───────────────┘
                                         ▼
                             [Member 4 Risk Engine]
                           (Multi-Modal Risk Fusion)
                                         │
                                         ▼
                             OVERALL RISK SCORE (0-100)
                              RISK LEVEL & EXPLANATION
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 [Member 5 Module]               [Member 6 Module]
                 Frontend Dashboard             Real-Time Alert Response
```

---

## 🔍 Conversation Analysis Methodology

Nexora employs a **Two-Stage Contextual & Rule-Based NLP Pipeline** designed for high-precision, low-latency hackathon prototype demonstration:

> [!NOTE]
> The current NLP implementation is a contextual rule-based system optimized for real-time hackathon demonstrations and is not a clinically or scientifically validated statistical probability model.

### Stage 1: Primary Behavioral Detection (18 Categories)
Analyzes sentence structures, intent patterns, and contextual suppressors to detect 18 primary risk behaviors:

- **Contextual False-Positive Handling**: Distinguishes between scammer demands ("*Tell me your OTP immediately*") and user statements citing security rules ("*The bank told me never to share my OTP*").
- **Deduplication**: Prevents repeated suspicious phrases from double-counting identical category scores.
- **18 Analyzed Suspicious Behaviors**:
  1. **OTP Request**: Demands for passcodes or authentication codes.
  2. **Money Transfer Request**: Direct requests for wire, UPI, or funds transfers.
  3. **Password / PIN Request**: Demands for account passwords, ATM PINs, or credentials.
  4. **Bank Credential Request**: Asking for bank account numbers, CVVs, or netbanking info.
  5. **Card Information Request**: Asking for credit/debit card numbers or expiry dates.
  6. **Remote Access Request**: Asking to install remote desktop tools (AnyDesk, TeamViewer).
  7. **Software Installation Request**: Instructing user to install applications or APK files.
  8. **Possible Bank Impersonation**: Claiming to represent bank or fraud department.
  9. **Police / Government Impersonation**: Claiming to be police, CBI, tax, or legal official.
  10. **Technical Support Impersonation**: Claiming to represent customer care or IT helpdesk.
  11. **Account Blocking Threat**: Threatening immediate account or card blockage.
  12. **Fear / Threat Language**: Using arrest warnings, legal action, or penalty threats.
  13. **Unusual Urgency / Pressure**: Pressuring victim to act immediately without verifying.
  14. **Suspicious Link**: Directing victim to open short links or phishing URLs.
  15. **Bypass Verification Attempt**: Instructing victim not to visit branch or contact support.
  16. **Secrecy Request**: Instructing victim to keep call secret from family or bank.
  17. **Confidential Information Request**: Demands for personal identity or sensitive data.
  18. **Urgent Payment Request**: Demands for quick payment under pretext of emergency.

---

### Stage 2: Compound Risk Analysis Layer

After first-stage detectors evaluate the transcript, the **Compound Risk Analysis Layer** evaluates combinations of detected categories to identify sophisticated multi-vector attack tactics. 

> [!IMPORTANT]
> Compound factors are derived directly from combinations of first-stage detected categories. To maintain balanced scoring, at most **one** compound factor is added per conversation.

#### Evaluated Compound Patterns

1. **Coordinated Financial Social-Engineering Pattern** (+25 Score):
   - **Trigger**: `bank_impersonation` + (`otp_request` | `bank_credential_request` | `card_info_request` | `password_pin_request`) + (`financial_transfer` | `urgent_payment`).
   - **Evidence**: *"Bank impersonation combined with credential collection and financial action request"*
2. **Coordinated Remote-Access Scam Pattern** (+25 Score):
   - **Trigger**: `tech_support_impersonation` + (`remote_access_request` | `software_install_request`).
   - **Evidence**: *"Technical support impersonation combined with remote access or software installation request"*
3. **Coercive Impersonation Pattern** (+20 Score):
   - **Trigger**: Any Impersonation + (`account_blocking_threat` | `fear_threat_language`) + (`unusual_urgency` | `urgent_payment`).
   - **Evidence**: *"Impersonation combined with threat language and immediate pressure"*
4. **Coordinated Social-Engineering Pattern** (+20 Score):
   - **Trigger**: Any Impersonation + Sensitive Information Request + (`unusual_urgency` | `secrecy_request` | `bypass_verification`).
   - **Evidence**: *"Impersonation combined with sensitive information request and manipulation tactics"*

---

## 📊 Risk Scoring Methodology & Weights

### 1. Voice AI Score Conventions
- `voice_authenticity_score` ($S_{\text{voice}}$): Confidence that voice is genuine ($1.0 = \text{genuine}$, $0.0 = \text{cloned voice}$).
  $$\text{voice\_risk} = (1.0 - S_{\text{voice}}) \times 100$$
- `speaker_verification_score` ($S_{\text{speaker}}$): Match confidence with claimed identity ($1.0 = \text{matched}$, $0.0 = \text{imposter}$).
  $$\text{speaker\_risk} = (1.0 - S_{\text{speaker}}) \times 100$$

### 2. Multi-Modal Fusion Formula
Weights are transparently configured in `config.py`:
- Voice Authenticity Risk Weight: **30%**
- Speaker Verification Risk Weight: **30%**
- Conversation Behavior Risk Weight: **40%**

$$\text{Overall Risk Score} = \text{round}\Big((0.30 \times \text{voice\_risk}) + (0.30 \times \text{speaker\_risk}) + (0.40 \times \text{conversation\_risk})\Big)$$

The conversation risk score is bounded to 0–100 (`min(100, raw_score)`).

### 3. Risk Levels & Action Mapping
| Score Range | Risk Level | Recommended Action | Operator Guidance |
| :---: | :---: | :---: | :--- |
| **0 – 39** | `LOW` | `ALLOW_CALL` | Normal conversation detected. No intervention. |
| **40 – 69** | `MEDIUM` | `VERIFY_IDENTITY` | Suspicious phrasing or voice uncertainty. Secondary verification advised. |
| **70 – 100** | `HIGH` | `CHALLENGE_OR_BLOCK` | Severe impersonation/cloning threat. Alert operator, issue challenge, or drop call. |

---

## 🔌 API Documentation

### `POST /analyze`

Evaluates transcript and voice AI signals to generate real-time risk scores, compound factors, and recommendations.

#### Request Body
```json
{
  "transcript": "I'm calling from your bank. Your account will be blocked. Tell me your OTP and transfer ₹20,000 immediately.",
  "voice_authenticity_score": 0.35,
  "speaker_verification_score": 0.40
}
```

#### Actual Live Output (Scenario 3 Response)
```json
{
  "overall_risk_score": 78,
  "risk_level": "HIGH",
  "conversation_risk_score": 100,
  "voice_risk": 65.0,
  "speaker_risk": 60.0,
  "risk_factors": [
    {
      "factor": "OTP request",
      "severity": "HIGH",
      "evidence": "Tell me your OTP and transfer ₹20,000 immediately",
      "score": 35
    },
    {
      "factor": "Money transfer request",
      "severity": "HIGH",
      "evidence": "Tell me your OTP and transfer ₹20,000 immediately",
      "score": 35
    },
    {
      "factor": "Possible bank impersonation",
      "severity": "HIGH",
      "evidence": "I'm calling from your bank",
      "score": 25
    },
    {
      "factor": "Account blocking threat",
      "severity": "MEDIUM-HIGH",
      "evidence": "Your account will be blocked",
      "score": 20
    },
    {
      "factor": "Unusual urgency / pressure",
      "severity": "MEDIUM-HIGH",
      "evidence": "Tell me your OTP and transfer ₹20,000 immediately",
      "score": 15
    },
    {
      "factor": "Coordinated financial social-engineering pattern",
      "severity": "HIGH",
      "evidence": "Bank impersonation combined with credential collection and financial action request",
      "score": 25
    }
  ],
  "explanation": "HIGH RISK (78/100) — Impersonation attack likely. Reasons: Multiple suspicious behaviors detected (OTP request, Money transfer request, Possible bank impersonation, Account blocking threat, Unusual urgency / pressure, Coordinated financial social-engineering pattern); High synthetic voice clone probability (Voice Risk: 65%); Speaker identity verification failed (Speaker Risk: 60%).",
  "recommended_action": "CHALLENGE_OR_BLOCK"
}
```

---

## 🧪 Verified Demo Scenarios & Test Suite

### Automated Unit & Integration Tests
The project includes **22 automated tests** covering individual behavior detectors, compound risk detection, contextual false-positive suppression, score normalization, multi-modal risk engine fusion, and FastAPI endpoint routes.

Run tests:
```bash
./venv/bin/pytest tests/ -v
# Output: 22 passed in 0.33s
```

### Hackathon Demo Scenarios Execution Summary

| Scenario | Transcript | Conv. Risk | Overall Score | Risk Level | Recommended Action | Compound Factor Detected |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Normal** | *"Hey, are we still meeting at 5 today?"* | 0% | **4 / 100** | `LOW` | `ALLOW_CALL` | None |
| **2. Suspicious** | *"Can you send me your account details? I need to verify something."* | 30% | **42 / 100** | `MEDIUM` | `VERIFY_IDENTITY` | None |
| **3. Bank Impersonation** | *"I'm calling from your bank. Your account will be blocked. Tell me your OTP and transfer ₹20,000 immediately."* | 100% | **78 / 100** | `HIGH` | `CHALLENGE_OR_BLOCK` | **Coordinated financial social-engineering pattern** |
| **4. Remote Access** | *"I'm from technical support. Install this application and give me remote access to your computer."* | 100% | **84 / 100** | `HIGH` | `CHALLENGE_OR_BLOCK` | **Coordinated remote-access scam pattern** |
| **5. Contextual OTP** | *"The bank told me never to share my OTP with anyone over the phone."* | 0% | **4 / 100** | `LOW` | `ALLOW_CALL` | None *(Contextually Suppressed)* |

---

## 🚀 Running Instructions

```bash
# Navigate to risk-analysis directory
cd risk-analysis

# Run verified pytest test suite (22 tests)
./venv/bin/pytest tests/ -v

# Run interactive demo script
./venv/bin/python run_demo_analysis.py

# Start FastAPI web server (http://localhost:8000)
./venv/bin/python app.py
```

---

## 🤝 Integration Contract for Team Members

- **Member 2 (Voice Spoof Detection)**: Pass `voice_authenticity_score` float ($1.0 = \text{genuine}$, $0.0 = \text{clone}$).
- **Member 3 (Speaker Verification)**: Pass `speaker_verification_score` float ($1.0 = \text{match}$, $0.0 = \text{imposter}$).
- **Member 5 (Frontend Dashboard)**: Consume `overall_risk_score`, `risk_level`, `risk_factors`, and `explanation` from `POST /analyze`.
- **Member 6 (Real-Time Alert Response)**: Consume `recommended_action` (`ALLOW_CALL`, `VERIFY_IDENTITY`, `CHALLENGE_OR_BLOCK`) for immediate response execution.

---

## 🔒 Security & Privacy Notice

- **No Permanent Storage**: Call transcripts are processed transiently in memory and discarded.
- **Data Protection**: Real authentication codes, PINs, or credentials are never logged or stored.
- **Synthetic Data**: Demonstrations use strictly synthetic hackathon test samples.
