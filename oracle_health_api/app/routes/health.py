from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database import check_connection
from app.schemas.health import HealthResponse, HealthStatus

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> JSONResponse:
    is_healthy, detail = await check_connection()
    status = HealthStatus.healthy if is_healthy else HealthStatus.unhealthy
    http_status = 200 if is_healthy else 503
    body = HealthResponse(status=status, database="oracle", detail=detail)
    return JSONResponse(content=body.model_dump(), status_code=http_status)
