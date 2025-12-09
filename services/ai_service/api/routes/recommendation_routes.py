"""HTTP routes exposing recommendation functionality."""

from fastapi import APIRouter, Request, status

from shared.models.recommendation import RecommendationRequest, RecommendationResponse

from ...services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
async def create_recommendation(request_payload: RecommendationRequest, request: Request) -> RecommendationResponse:
    """Return a heating or ventilation recommendation."""
    service = _resolve_service(request)
    return service.buildRecommendation(request_payload)


def _resolve_service(request: Request) -> RecommendationService:
    """Fetch the recommendation service from application state."""
    service: RecommendationService = request.app.state.recommendation_service
    return service

