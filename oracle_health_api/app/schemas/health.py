from enum import Enum
from pydantic import BaseModel


class HealthStatus(str, Enum):
    healthy = "healthy"
    unhealthy = "unhealthy"


class HealthResponse(BaseModel):
    status: HealthStatus
    database: str
    detail: str | None = None
