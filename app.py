import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from speaker_verification.config import settings
from speaker_verification.model import ModelManager
from speaker_verification.routes import router as speaker_router
from speaker_verification.exceptions import (
    SpeakerVerificationError,
    SpeakerNotFoundError,
    EnrollmentNotFoundError,
    EmptyAudioError,
    InsufficientSpeechError,
    CorruptedAudioError,
    InvalidAudioError,
    ModelLoadingError,
    InferenceError,
)
from speaker_verification.schemas import ErrorDetail

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nexora.speaker_verification")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager. Loads model once on startup and cleans up on shutdown.
    """
    logger.info("Initializing Nexora Speaker Verification Service...")
    # Eagerly initialize model singleton on startup
    try:
        ModelManager.get_model()
    except Exception as exc:
        logger.error(f"Failed model startup initialization: {exc}")
    yield
    logger.info("Shutting down Nexora Speaker Verification Service.")


app = FastAPI(
    title="Nexora Speaker Verification API",
    description="Production-quality speaker verification module using ECAPA-TDNN embeddings & Cosine Similarity.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Domain Exception Handlers (Clean JSON API Errors instead of unhandled stack traces)

@app.exception_handler(SpeakerNotFoundError)
@app.exception_handler(EnrollmentNotFoundError)
async def speaker_not_found_handler(request: Request, exc: SpeakerVerificationError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorDetail(
            error_code=exc.code,
            message=exc.message,
            speaker_id=getattr(exc, "speaker_id", None),
        ).model_dump(),
    )


@app.exception_handler(EmptyAudioError)
@app.exception_handler(InsufficientSpeechError)
@app.exception_handler(CorruptedAudioError)
@app.exception_handler(InvalidAudioError)
async def audio_error_handler(request: Request, exc: SpeakerVerificationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorDetail(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(ModelLoadingError)
@app.exception_handler(InferenceError)
async def model_error_handler(request: Request, exc: SpeakerVerificationError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorDetail(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(SpeakerVerificationError)
async def generic_speaker_verification_handler(request: Request, exc: SpeakerVerificationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorDetail(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "nexora-speaker-verification",
        "threshold": settings.verification_threshold,
        "use_mock_model": settings.use_mock_model,
    }


# Include Router
app.include_router(speaker_router)
