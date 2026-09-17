"""FastAPI server for Yomeru ML sidecar."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.ocr import OCRError, OCRResult, recognize_base64
from services.tokenizer import Token, tokenize
from services.translator import TranslationError, translate

app = FastAPI(
    title="Yomeru ML Sidecar",
    description="Python ML engine for Japanese manga/VN translation",
    version="0.1.0",
)


class ProcessImageRequest(BaseModel):
    """Request model for image processing."""

    image: str = Field(..., description="Base64-encoded image string")


class TokenResponse(BaseModel):
    """Response model for a single token."""

    surface: str
    lemma: str
    reading: str
    pos: str


class ProcessImageResponse(BaseModel):
    """Response model for image processing."""

    raw_text: str
    translated_text: str
    tokens: list[TokenResponse]
    confidence: float = Field(
        ..., description="OCR confidence score (0.0 to 1.0). Low scores suggest multiple regions."
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str | None = None


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "online"}


@app.post(
    "/process-image",
    response_model=ProcessImageResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def process_image(request: ProcessImageRequest) -> ProcessImageResponse:
    """Process a manga image and return extracted text, translation, and tokens.

    Accepts a base64-encoded image and returns:
    - raw_text: Extracted Japanese text via OCR
    - translated_text: English translation
    - tokens: Morphological analysis of the raw text
    - confidence: OCR confidence score (0.0-1.0)
    """
    if not request.image:
        raise HTTPException(status_code=400, detail="Image field is required")

    try:
        ocr_result: OCRResult = recognize_base64(request.image)
    except OCRError as e:
        raise HTTPException(status_code=400, detail=f"OCR failed: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected OCR error: {e}") from e

    if not ocr_result.text:
        return ProcessImageResponse(
            raw_text="",
            translated_text="",
            tokens=[],
            confidence=ocr_result.confidence,
        )

    try:
        translated_text = translate(ocr_result.text)
    except TranslationError as e:
        translated_text = f"[Translation error: {e}]"
    except Exception as e:
        translated_text = f"[Unexpected translation error: {e}]"

    try:
        tokens = tokenize(ocr_result.text)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tokenization failed: {e}"
        ) from e

    return ProcessImageResponse(
        raw_text=ocr_result.text,
        translated_text=translated_text,
        tokens=[TokenResponse(**t.__dict__) for t in tokens],
        confidence=ocr_result.confidence,
    )
