# Nexora Speaker Verification Module

> **Component Responsibilities & Boundaries**  
> The Speaker Verification module is responsible solely for **Speaker Identity Matching** (determining if an incoming call voice matches a registered speaker profile).  
> **Anti-spoofing, voice deepfake detection, synthetic voice detection, and voice authenticity classification are strictly handled outside of this module by Team Member 2.**

---

## Technical Overview

### 1. Speaker Verification vs Voice Authenticity Detection
- **Speaker Verification (Identity Verification)**: Answers *"Who is speaking?"* by comparing the acoustic voice characteristics of an incoming speaker against an enrolled biometric template ($u_{\text{enrolled}}$ vs $v_{\text{incoming}}$).
- **Voice Authenticity Detection (Anti-Spoofing)**: Answers *"Is this a real human or a AI-generated voice clone / deepfake?"* regardless of identity.

---

### 2. Neural Architecture: ECAPA-TDNN
This module utilizes **ECAPA-TDNN** (*Emphasized Channel Attention, Propagation and Aggregation in Time-Delay Neural Network*), a state-of-the-art architecture for speaker recognition.

#### Why ECAPA-TDNN?
- **Squeeze-and-Excitation (SE) Blocks**: Rescales channel feature maps dynamically to focus on speaker-discriminative formant structures.
- **Multi-layer Feature Aggregation (MFA)**: Combines representations across shallow and deep layers to capture both high-frequency pitch and high-level temporal dynamics.
- **192-Dimensional Compact Embeddings**: Compresses speech waveforms into a fixed-length 192-dimensional vector.

---

## System Architecture & Pipeline

```
Incoming Audio Byte Stream
          ↓
Audio Decoding & Preprocessing (WAV, MP3, FLAC, OGG -> 16kHz Mono Float32)
          ↓
Voice Activity Detection (Energy VAD / Speech Segment Extraction)
          ↓
ECAPA-TDNN Neural Network (`speechbrain/spkrec-ecapa-voxceleb`)
          ↓
192-Dim Speaker Embedding Vector
          ↓
L2 Vector Normalization ($v_{\text{norm}} = \frac{v}{\|v\|_2}$)
          ↓
Cosine Similarity ($S = u_{\text{enrolled}} \cdot v_{\text{incoming}}$)
          ↓
Threshold-Based Decision Boundary ($S \ge \tau$)
          ↓
Calibrated Confidence Calculation
          ↓
Nexora Risk Engine Signal Generation
```

---

## Math & Algorithms

### 1. L2 Vector Normalization
Every extracted 192-dimensional embedding is normalized to unit length:
$$v_{\text{norm}} = \frac{v}{\|v\|_2} = \frac{v}{\sqrt{\sum_{i=1}^{192} v_i^2}}$$

### 2. Cosine Similarity Score
The similarity score $S \in [-1.0, 1.0]$ between the enrolled speaker template $u$ and the incoming call embedding $v$ is computed via vector dot-product:
$$S(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2} = \sum_{i=1}^{192} u_i \cdot v_i$$

### 3. Verification Decision & Threshold Boundary
$$\text{verified} = \begin{cases} \text{true} & \text{if } S(u, v) \ge \tau \\ \text{false} & \text{if } S(u, v) < \tau \end{cases}$$
- Default threshold $\tau = 0.70$ (configurable via environment variable `SPEAKER_VERIFICATION_THRESHOLD`).

### 4. Confidence Estimation
Confidence represents the decision boundary certainty ($C \in [0.0, 1.0]$):
- When $S \ge \tau$: $C = 0.50 + 0.50 \times \frac{S - \tau}{1.0 - \tau}$
- When $S < \tau$: $C = 0.50 - 0.50 \times \frac{\tau - S}{\tau - (-1.0)}$

---

## API Reference

### 1. POST `/speaker/enroll`
Enrolls a new genuine speaker with reference audio.

**Form Data**:
- `speaker_id` (string, required): Unique identifier for the speaker.
- `file` (binary, required): Audio file (WAV, MP3, FLAC, OGG, M4A).

**Response (201 Created)**:
```json
{
  "speaker_id": "user_12345",
  "status": "enrolled",
  "message": "Speaker 'user_12345' successfully enrolled.",
  "timestamp": "2026-09-14T20:00:00Z"
}
```

---

### 2. POST `/speaker/verify`
Verifies an incoming speaker against an enrolled template.

**Form Data**:
- `speaker_id` (string, required): Target speaker ID.
- `file` (binary, required): Incoming audio clip.
- `threshold` (float, optional): Custom decision threshold override.

**Response (200 OK)**:
```json
{
  "speaker_id": "user_12345",
  "verified": true,
  "similarity_score": 0.8742,
  "threshold": 0.7,
  "confidence": 0.9123,
  "model": "ECAPA-TDNN"
}
```

---

### 3. GET `/speaker/{speaker_id}`
Checks whether a speaker is enrolled.

**Response (200 OK)**:
```json
{
  "speaker_id": "user_12345",
  "enrolled": true
}
```

---

### 4. POST `/speaker/risk-signal`
Produces a machine-readable payload for integration with Nexora's Risk Engine.

**Response (200 OK)**:
```json
{
  "signal": "speaker_verification",
  "speaker_verified": true,
  "similarity_score": 0.8742,
  "confidence": 0.9123
}
```

---

## Risk Engine Integration

The Risk Engine consumes the output of this module alongside other security signals:

```json
{
  "call_id": "call_987654",
  "signals": {
    "speaker_verification": {
      "signal": "speaker_verification",
      "speaker_verified": true,
      "similarity_score": 0.8742,
      "confidence": 0.9123
    },
    "voice_authenticity": {
      "is_deepfake": false,
      "spoof_probability": 0.02
    },
    "conversation_risk": {
      "urgency_score": 0.15,
      "otp_requested": false
    }
  }
}
```

---

## Security & Biometric Protection

1. **No Raw Audio Storage**: Raw voice recordings are discarded immediately after embedding generation.
2. **Encrypted Biometric Vectors**: Embedded vectors are saved as binary `.npy` arrays with strict file permissions (`0o600`).
3. **No PII Logging**: Embeddings and raw audio are excluded from application logs.
4. **Input Path Sanitization**: Prevents path traversal vulnerabilities on `speaker_id`.

---

## Environment Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `SPEAKER_VERIFICATION_THRESHOLD` | Decision boundary for identity match | `0.70` |
| `SPEAKER_EMBEDDING_DIR` | Secure disk directory for speaker vectors | `./data/embeddings` |
| `SPEAKER_MODEL_NAME` | Pretrained SpeechBrain model | `speechbrain/spkrec-ecapa-voxceleb` |
| `USE_MOCK_MODEL` | Enable fast mock model for testing | `false` |
| `SPEAKER_MODEL_DEVICE` | Compute device (`cpu`, `cuda`, `mps`) | `cpu` |

---

## How to Run & Demonstrate Locally

### 1. Setup Virtual Environment
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
pytest -v tests/
```

### 3. Launch FastAPI Server
```bash
uvicorn app:app --reload --port 8000
```

### 4. Local API Curl Commands

**Enroll Speaker**:
```bash
curl -X POST "http://localhost:8000/speaker/enroll" \
  -F "speaker_id=user101" \
  -F "file=@sample_voice.wav"
```

**Verify Speaker**:
```bash
curl -X POST "http://localhost:8000/speaker/verify" \
  -F "speaker_id=user101" \
  -F "file=@sample_voice.wav"
```

**Fetch Risk Signal**:
```bash
curl -X POST "http://localhost:8000/speaker/risk-signal" \
  -F "speaker_id=user101" \
  -F "file=@sample_voice.wav"
```
