from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch settings before the app is imported so no real .env is needed
import app.config as _cfg

_cfg.settings.oracle_user = "test"
_cfg.settings.oracle_password = "test"
_cfg.settings.oracle_dsn = "localhost:1521/XEPDB1"

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@patch("app.routes.health.check_connection", new_callable=AsyncMock)
def test_health_healthy(mock_check, client):
    mock_check.return_value = (True, "Oracle connection is healthy")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("app.routes.health.check_connection", new_callable=AsyncMock)
def test_health_unhealthy(mock_check, client):
    mock_check.return_value = (False, "ORA-12541: TNS no listener")
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"
    assert "ORA-12541" in response.json()["detail"]
