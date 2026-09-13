"""
FastAPI Microservice Application for Nexora Risk Analysis Engine (Member 4).
"""

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import AnalysisRequest, AnalysisResponse
from risk_engine import RiskEngine

app = FastAPI(
    title="Nexora - Conversation & Risk Analysis API",
    description="Real-Time Risk Scoring Engine for Voice Cloning & Impersonation Attack Prevention (SIH22104)",
    version="1.0.0"
)

# Enable CORS for Member 5 Dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate single global RiskEngine instance
engine = RiskEngine()


@app.get("/")
def read_root():
    """Root endpoint detailing module purpose and health."""
    return {
        "project": "Nexora",
        "module": "Member 4 - Conversation & Risk Analysis + Risk Scoring",
        "problem_statement": "SIH22104 - AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attack",
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for system monitoring and service discovery."""
    return {"status": "healthy", "service": "nexora-risk-analysis"}


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_call(request: AnalysisRequest):
    """
    Main endpoint analyzing transcript and voice AI signals to generate
    overall risk score, risk level, risk factors, explanation, and recommended action.
    """
    try:
        response = engine.evaluate(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis error: {str(e)}")


@app.get("/scenarios")
def get_demo_scenarios():
    """Returns the standard pre-defined hackathon test scenarios."""
    scenarios_file = Path(__file__).parent / "sample_data" / "sample_conversations.json"
    if scenarios_file.exists():
        with open(scenarios_file, "r") as f:
            return json.load(f)
    return {"error": "Sample scenarios file not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
