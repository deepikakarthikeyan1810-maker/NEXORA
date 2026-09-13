# Nexora — Real-Time Risk Analysis Engine (Member 4 Module)

> **SIH Problem Statement**: SIH22104 – AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attack  
> **Project Name**: Nexora  
> **Module Owner**: Member 4 — Conversation & Risk Analysis + Risk-Based Scoring  

---

## 📌 Module Purpose & Overview

The **Conversation & Risk Analysis Engine** is the core decision-making module of the **Nexora** anti-impersonation platform. It performs real-time contextual NLP analysis on speech-to-text live transcripts and fuses these behavioral signals with voice authenticity (Member 2) and speaker verification (Member 3) scores. 

The module answers seven critical questions in real-time during a call:
1. **What is the caller asking the victim to do?** (Intent & behavior extraction)
2. **Is the conversation suspicious?** (Pattern matching & contextual scoring)
3. **What risk factors are present?** (Categorized evidence-backed threat list)
4. **How risky is the conversation?** (Normalized 0–100 conversation score)
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
           │                           │                 │
           └─────────────┬─────────────┘                 │
                         ▼                               │
                 MOCK / LIVE SCORES                      │
                         │                               │
                         └───────────────┬───────────────┘
                                         ▼
                             [Member 4 Risk Engine]
                           (Conversation & Risk Analysis)
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

Unlike naive keyword spotters, Nexora uses **Contextual & Rule-Based NLP** to evaluate intent, sentence structure, and conversational role:

- **Contextual False-Positive Handling**: Distinguishes between scammer demands ("*Tell me your OTP immediately*") and user statements citing security rules ("*The bank told me never to share my OTP*").
- **Deduplication**: Prevents repeated suspicious phrases from artificially inflating scores.
- **Analyzed Suspicious Behaviors**:
  1. OTP Requests
  2. Financial / Money Transfer Demands
  3. Password / PIN Requests
  4. Bank & Account Credential Requests
  5. Debit / Credit Card Information Requests
  6. Urgent Payment Demands
  7. Account Blocking / Suspension Threats
  8. Identity Impersonation (General / Executive)
  9. Bank / Customer-Support Impersonation
  10. Police / Government / Tax Impersonation
  11. Technical Support Impersonation
  12. Remote Access Software Requests (AnyDesk, TeamViewer)
  13. Third-party Software / APK Installation Requests
  14. Phishing / Suspicious Links
  15. Confidential Information Requests
  16. Pressure Tactics & Unusual Urgency
  17. Fear / Legal Threat Language
  18. Verification Bypass Attempts & Secrecy Requests

---

## 📊 Risk Scoring Methodology & Weights

### 1. Voice AI Score Conventions
- `voice_authenticity_score` ($S_{\text{voice}}$): Probability voice is genuine ($1.0 = \text{genuine}$, $0.0 = \text{cloned}$).
  $$\text{voice\_risk} = (1.0 - S_{\text{voice}}) \times 100$$
- `speaker_verification_score` ($S_{\text{speaker}}$): Match confidence with claimed identity ($1.0 = \text{matched}$, $0.0 = \text{imposter}$).
  $$\text{speaker\_risk} = (1.0 - S_{\text{speaker}}) \times 100$$

### 2. Multi-Modal Fusion Formula
Weights are transparently configured in `config.py`:
- Voice Authenticity Risk Weight: **30%**
- Speaker Verification Risk Weight: **30%**
- Conversation Behavior Risk Weight: **40%**

$$\text{Overall Risk Score} = \text{round}\Big((0.30 \times \text{voice\_risk}) + (0.30 \times \text{speaker\_risk}) + (0.40 \times \text{conversation\_risk})\Big)$$

### 3. Risk Levels & Action Mapping
| Score Range | Risk Level | Recommended Action | Operator Guidance |
| :---: | :---: | :---: | :--- |
| **0 – 39** | `LOW` | `ALLOW_CALL` | Normal conversation detected. No intervention. |
| **40 – 69** | `MEDIUM` | `VERIFY_IDENTITY` | Suspicious phrasing or voice uncertainty. Secondary verification advised. |
| **70 – 100** | `HIGH` | `CHALLENGE_OR_BLOCK` | Severe impersonation/cloning threat. Alert operator, issue challenge, or drop call. |

---

## 🔌 API Documentation

### `POST /analyze`

Evaluates transcript and voice AI signals to generate real-time risk scores and recommendations.

#### Request Body
```json
{
  "transcript": "I'm calling from your bank. Your account will be blocked. Give me the OTP and transfer ₹20,000 immediately.",
  "voice_authenticity_score": 0.35,
  "speaker_verification_score": 0.40
}
```

#### Response Body
```json
{
  "overall_risk_score": 89,
  "risk_level": "HIGH",
  "conversation_risk_score": 95,
  "voice_risk": 65.0,
  "speaker_risk": 60.0,
  "risk_factors": [
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
      "factor": "OTP request",
      "severity": "HIGH",
      "evidence": "Give me the OTP",
      "score": 35
    },
    {
      "factor": "Money transfer request",
      "severity": "HIGH",
      "evidence": "transfer ₹20,000 immediately",
      "score": 35
    }
  ],
  "explanation": "HIGH RISK (89/100) — Impersonation attack likely. Reasons: Multiple suspicious behaviors detected (Possible bank impersonation, Account blocking threat, OTP request, Money transfer request); High synthetic voice clone probability (Voice Risk: 65%); Speaker identity verification failed (Speaker Risk: 60%).",
  "recommended_action": "CHALLENGE_OR_BLOCK"
}
```

---

## 🧪 Demo Scenarios

The system includes 5 standard hackathon test scenarios (available via `GET /scenarios`):

| Scenario | Description | Expected Risk | Expected Action |
| :--- | :--- | :---: | :---: |
| **1. Normal** | *"Hey, are we still meeting at 5 today?"* | `LOW` | `ALLOW_CALL` |
| **2. Suspicious** | *"Can you send me your account details? I need to verify something."* | `MEDIUM` | `VERIFY_IDENTITY` |
| **3. Bank Impersonation** | *"I'm calling from your bank. Your account will be blocked. Tell me your OTP and transfer the money immediately."* | `HIGH` | `CHALLENGE_OR_BLOCK` |
| **4. Remote Access** | *"I'm from technical support. Install this application and give me remote access to your computer."* | `HIGH` | `CHALLENGE_OR_BLOCK` |
| **5. Contextual OTP** | *"The bank told me never to share my OTP with anyone over the phone."* | `LOW` | `ALLOW_CALL` |

---

## 🚀 Running & Testing Instructions

### 1. Install Dependencies
```bash
cd risk-analysis
pip install -r requirements.txt
```

### 2. Run Automated Unit & Integration Tests
```bash
pytest tests/ -v
```

### 3. Start FastAPI Server
```bash
python3 app.py
# Server starts at http://localhost:8000
# Interactive Swagger UI docs available at http://localhost:8000/docs
```

---

## 🤝 Integration Contract for Team Members

### For Member 2 (Voice Anti-Spoofing AI)
- Output your model's confidence that the caller's voice is authentic as a float between `0.0` (synthetic clone) and `1.0` (authentic voice).
- Pass this float in the API request as `voice_authenticity_score`.

### For Member 3 (Speaker Verification AI)
- Output your ECAPA-TDNN model's identity match score as a float between `0.0` (imposter) and `1.0` (matched speaker).
- Pass this float in the API request as `speaker_verification_score`.

### For Member 5 (Frontend Dashboard)
- Call `POST /analyze` with live audio STT transcripts and AI scores.
- Consume `overall_risk_score`, `risk_level`, `risk_factors`, and `explanation` for real-time visual telemetry.

### For Member 6 (Real-Time Alert Response)
- Listen to `recommended_action` (`ALLOW_CALL`, `VERIFY_IDENTITY`, `CHALLENGE_OR_BLOCK`) and `overall_risk_score` to trigger call intervention, IVR challenge prompts, or automated call termination.

---

## 🔒 Security & Privacy Notice

- **No Permanent Storage**: Live call transcripts are analyzed in memory and immediately discarded.
- **Data Protection**: Real passcodes, PINs, or credentials are never logged or stored.
- **Synthetic Data**: All test data and scenarios use strictly synthetic examples.
