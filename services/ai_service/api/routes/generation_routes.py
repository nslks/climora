"""HTTP routes exposing provider-neutral text generation."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from ai_service.api.dependencies import get_text_generation_service
from ai_service.services.text_generation_service import TextGenerationRequest, TextGenerationService

router = APIRouter(prefix="/generation", tags=["generation"])


class GenerateTextRequest(BaseModel):
    """Request body for provider-neutral text generation."""

    prompt: str = Field(..., description="Prompt forwarded to the configured LLM client.", min_length=1)
    response_format: str | None = Field(default=None, description="Optional provider-agnostic response format hint.")
    stream: bool = Field(default=False, description="Whether to request stream mode if the provider supports it.")
    options: Dict[str, Any] | None = Field(default=None, description="Optional provider options.")


class GenerateTextResponse(BaseModel):
    """API response containing generated text."""

    output_text: str


@router.post("/generate", response_model=GenerateTextResponse, status_code=status.HTTP_200_OK)
async def generate_text(
    payload: GenerateTextRequest,
    service: TextGenerationService = Depends(get_text_generation_service),
) -> GenerateTextResponse:
    """Generate text using the configured provider client."""
    result = service.generate_text(
        TextGenerationRequest(
            prompt=payload.prompt,
            response_format=payload.response_format,
            stream=payload.stream,
            options=payload.options,
        )
    )
    return GenerateTextResponse(output_text=result.output_text)
