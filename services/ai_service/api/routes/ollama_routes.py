"""HTTP routes exposing raw Ollama functionality."""

from typing import Any, Dict, cast

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

from ...services.ollama_service import OllamaPrompt, OllamaService

router = APIRouter(prefix="/ollama", tags=["ollama"])


class GenerateRequest(BaseModel):
    """Request body for Ollama generation."""

    prompt: str = Field(..., description="Prompt forwarded to Ollama.", min_length=1)
    format: str | None = Field(default=None, description="Optional Ollama output format (e.g. json).")
    stream: bool = Field(default=False, description="Request streaming responses directly from Ollama.")
    options: Dict[str, Any] | None = Field(
        default=None,
        description="Additional Ollama options (temperature, top_k, etc.).",
    )


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate(payload: GenerateRequest, request: Request) -> Dict[str, Any]:
    """Forward the prompt to Ollama and return the response."""
    service = _resolve_service(request)
    prompt = OllamaPrompt(
        prompt=payload.prompt,
        format=payload.format,
        stream=payload.stream,
        options=payload.options,
    )
    return service.generate(prompt)


def _resolve_service(request: Request) -> OllamaService:
    """Fetch the Ollama service from application state."""
    return cast(OllamaService, request.app.state.ollama_service)
