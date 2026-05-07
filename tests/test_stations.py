import os
# Must be set before any app imports so database.py picks it up
os.environ["DB_PATH"] = "test_worldradio.db"

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    # Wipe play events before each test for isolation
    db = await get_db()
    await db.execute("DELETE FROM play_events")
    await db.commit()
    await db.close()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_stations_known_country(client):
    """Should return up to 5 stations for a known country code."""
    response = await client.get("/api/stations/US")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    # Each station should have required fields
    for station in data:
        assert "name" in station
        assert "stream_url" in station
        assert "country_code" in station


@pytest.mark.asyncio
async def test_get_stations_invalid_code(client):
    """Single-letter or non-alpha codes should return 400."""
    response = await client.get("/api/stations/X")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_stations_unknown_country(client):
    """Valid format but no stations available should return 404."""
    response = await client.get("/api/stations/ZZ")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_log_play_event(client):
    """Logging a play event should return 201 with the event data."""
    response = await client.post(
        "/api/stations/play",
        params={
            "station_uuid": "us-1",
            "station_name": "NPR News",
            "country_code": "US",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["station_uuid"] == "us-1"
    assert data["country_code"] == "US"


@pytest.mark.asyncio
async def test_trending_reflects_play_events(client):
    """Trending endpoint should rank stations by play count."""
    # Log NPR twice, BBC once
    for _ in range(2):
        await client.post(
            "/api/stations/play",
            params={"station_uuid": "us-1", "station_name": "NPR News", "country_code": "US"},
        )
    await client.post(
        "/api/stations/play",
        params={"station_uuid": "gb-1", "station_name": "BBC Radio 1", "country_code": "GB"},
    )

    response = await client.get("/api/trending")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["station_uuid"] == "us-1"
    assert data[0]["play_count"] == 2
    assert data[1]["station_uuid"] == "gb-1"
    assert data[1]["play_count"] == 1
