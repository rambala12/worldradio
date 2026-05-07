from fastapi import APIRouter, HTTPException, Query
from app.radio_client import fetch_stations
from app.database import get_db
from app.schemas import Station, PlayEvent, TopStation
from datetime import datetime

router = APIRouter(tags=["stations"])


@router.get("/stations/{country_code}", response_model=list[Station])
async def get_stations(
    country_code: str,
    limit: int = Query(default=5, ge=1, le=20),
):
    """
    Return the top N radio stations for a given country code.
    Country code should be ISO 3166-1 alpha-2 (e.g. 'US', 'GB', 'JP').
    """
    if len(country_code) != 2 or not country_code.isalpha():
        raise HTTPException(status_code=400, detail="Country code must be a 2-letter ISO code.")

    stations = await fetch_stations(country_code.upper(), limit=limit)

    if not stations:
        raise HTTPException(
            status_code=404,
            detail=f"No stations found for country code '{country_code.upper()}'.",
        )

    return stations


@router.post("/stations/play", response_model=PlayEvent, status_code=201)
async def log_play(station_uuid: str, station_name: str, country_code: str):
    """
    Log a play event when a user starts streaming a station.
    This powers the trending / most-played features.
    """
    played_at = datetime.utcnow()

    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO play_events (country_code, station_uuid, station_name, played_at)
            VALUES (?, ?, ?, ?)
            """,
            (country_code.upper(), station_uuid, station_name, played_at),
        )
        await db.commit()
    finally:
        await db.close()

    return PlayEvent(
        country_code=country_code.upper(),
        station_uuid=station_uuid,
        station_name=station_name,
        played_at=played_at,
    )


@router.get("/trending", response_model=list[TopStation])
async def get_trending(limit: int = Query(default=10, ge=1, le=50)):
    """
    Return the globally most-played stations based on logged play events.
    This is the 'now trending' feature — powered by our own play data.
    """
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT
                station_uuid,
                station_name,
                country_code,
                COUNT(*) as play_count
            FROM play_events
            GROUP BY station_uuid
            ORDER BY play_count DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
    finally:
        await db.close()

    return [
        TopStation(
            station_uuid=row["station_uuid"],
            station_name=row["station_name"],
            country_code=row["country_code"],
            play_count=row["play_count"],
        )
        for row in rows
    ]
