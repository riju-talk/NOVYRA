import pytest
from httpx import AsyncClient
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_health_check_integration():
    """Verify that the health check endpoint returns correctly with middleware."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    # We expect some services might be disconnected in this test environment
    print(f"\nHealth response: {data}")

@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "service" in response.json()

@pytest.mark.asyncio
async def test_error_handling_middleware():
    """Verify that the error handling middleware catches crashes."""
    # We can't easily force a crash without a specific 'crash' route, 
    # but we can try an invalid route and see if we get the X-Request-ID header.
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/non-existent-route")
    
    assert "X-Request-ID" in response.headers
    assert response.status_code == 404
