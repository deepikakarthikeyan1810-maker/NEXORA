import logging
from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile, status, Query
from fastapi.responses import JSONResponse

from speaker_verification.service import SpeakerVerificationService
from speaker_verification.schemas import (
    EnrollmentResponse,
    VerificationResponse,
    SpeakerStatusResponse,
    RiskEngineSignal,
    ErrorDetail,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speaker", tags=["Speaker Verification"])


def get_service() -> SpeakerVerificationService:
    return SpeakerVerificationService()


@router.post(
    "/enroll",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll a genuine speaker",
    description="Extracts and securely stores an ECAPA-TDNN speaker embedding for identity matching.",
)
async def enroll_speaker(
    speaker_id: str = Form(..., description="Unique speaker identifier"),
    file: UploadFile = File(..., description="Reference audio recording file"),
):
    audio_bytes = await file.read()
    response = get_service().enroll_speaker(speaker_id=speaker_id, audio_bytes=audio_bytes)
    return response


@router.post(
    "/verify",
    response_model=VerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify an incoming speaker",
    description="Compares incoming audio against enrolled ECAPA-TDNN embedding via Cosine Similarity.",
)
async def verify_speaker(
    speaker_id: str = Form(..., description="Enrolled speaker identifier"),
    file: UploadFile = File(..., description="Incoming call audio file"),
    threshold: Optional[float] = Form(None, description="Optional decision threshold override"),
):
    audio_bytes = await file.read()
    response = get_service().verify_speaker(
        speaker_id=speaker_id,
        audio_bytes=audio_bytes,
        threshold_override=threshold,
    )
    return response


@router.get(
    "/{speaker_id}",
    response_model=SpeakerStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check speaker enrollment status",
    description="Returns whether a speaker embedding is currently enrolled.",
)
async def get_speaker_status(speaker_id: str):
    response = get_service().get_speaker_status(speaker_id=speaker_id)
    return response


@router.delete(
    "/{speaker_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete speaker enrollment",
    description="Removes enrolled speaker embedding record.",
)
async def delete_speaker(speaker_id: str):
    get_service().delete_speaker(speaker_id=speaker_id)
    return {"status": "deleted", "speaker_id": speaker_id}


@router.post(
    "/risk-signal",
    response_model=RiskEngineSignal,
    status_code=status.HTTP_200_OK,
    summary="Generate Risk Engine Signal",
    description="Produces machine-readable signal payload for Nexora Risk Engine consumption.",
)
async def get_risk_signal(
    speaker_id: str = Form(..., description="Target speaker ID"),
    file: UploadFile = File(..., description="Incoming audio file"),
    threshold: Optional[float] = Form(None, description="Optional custom threshold"),
):
    audio_bytes = await file.read()
    signal_payload = get_service().get_risk_signal(
        speaker_id=speaker_id,
        audio_bytes=audio_bytes,
        threshold_override=threshold,
    )
    return signal_payload
