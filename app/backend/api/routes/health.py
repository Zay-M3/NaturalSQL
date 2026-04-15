from fastapi import APIRouter

from schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
