from pydantic import BaseModel
from datetime import datetime


class Station(BaseModel):
    station_uuid: str
    name: str
    country: str
    country_code: str
    language: str
    stream_url: str
    favicon: str
    tags: list[str]
    votes: int
    bitrate: int

    class Config:
        from_attributes = True


class PlayEvent(BaseModel):
    country_code: str
    station_uuid: str
    station_name: str
    played_at: datetime


class TopStation(BaseModel):
    station_uuid: str
    station_name: str
    country_code: str
    play_count: int
