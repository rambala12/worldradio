import httpx
from app.schemas import Station

RADIO_BROWSER_BASE = "https://de1.api.radio-browser.info/json"
HEADERS = {"User-Agent": "WorldRadioApp/1.0"}

# Mock data used as fallback during development / testing
MOCK_STATIONS: dict[str, list[dict]] = {
    "US": [
        {"station_uuid": "us-1", "name": "NPR News", "country": "United States", "country_code": "US", "language": "english", "url_resolved": "https://npr-ice.streamguys1.com/live.mp3", "favicon": "", "tags": "news,public", "votes": 9800, "bitrate": 128},
        {"station_uuid": "us-2", "name": "KEXP 90.3", "country": "United States", "country_code": "US", "language": "english", "url_resolved": "https://kexp-mp3-128.streamguys1.com/kexp128.mp3", "favicon": "", "tags": "indie,alternative", "votes": 8700, "bitrate": 128},
        {"station_uuid": "us-3", "name": "Jazz24", "country": "United States", "country_code": "US", "language": "english", "url_resolved": "https://live.wostreaming.net/manifest/ppm-jazz24mp3-ibc1.m3u8", "favicon": "", "tags": "jazz", "votes": 7500, "bitrate": 128},
        {"station_uuid": "us-4", "name": "Radio Paradise", "country": "United States", "country_code": "US", "language": "english", "url_resolved": "https://stream.radioparadise.com/mp3-128", "favicon": "", "tags": "eclectic,rock", "votes": 7000, "bitrate": 128},
        {"station_uuid": "us-5", "name": "SomaFM Groove Salad", "country": "United States", "country_code": "US", "language": "english", "url_resolved": "https://ice1.somafm.com/groovesalad-128-mp3", "favicon": "", "tags": "ambient,chillout", "votes": 6500, "bitrate": 128},
    ],
    "GB": [
        {"station_uuid": "gb-1", "name": "BBC Radio 1", "country": "United Kingdom", "country_code": "GB", "language": "english", "url_resolved": "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one", "favicon": "", "tags": "pop,chart", "votes": 9500, "bitrate": 128},
        {"station_uuid": "gb-2", "name": "BBC Radio 4", "country": "United Kingdom", "country_code": "GB", "language": "english", "url_resolved": "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm", "favicon": "", "tags": "talk,news", "votes": 8900, "bitrate": 128},
        {"station_uuid": "gb-3", "name": "Classic FM", "country": "United Kingdom", "country_code": "GB", "language": "english", "url_resolved": "https://media-ice.musicradio.com/ClassicFMMP3", "favicon": "", "tags": "classical", "votes": 7800, "bitrate": 128},
        {"station_uuid": "gb-4", "name": "NTS Radio", "country": "United Kingdom", "country_code": "GB", "language": "english", "url_resolved": "https://stream-relay-geo.ntslive.net/stream", "favicon": "", "tags": "eclectic,experimental", "votes": 6800, "bitrate": 128},
        {"station_uuid": "gb-5", "name": "Rinse FM", "country": "United Kingdom", "country_code": "GB", "language": "english", "url_resolved": "https://stream.rinse.fm:8400/rinse.mp3", "favicon": "", "tags": "dance,grime", "votes": 5900, "bitrate": 128},
    ],
    "JP": [
        {"station_uuid": "jp-1", "name": "NHK World Radio Japan", "country": "Japan", "country_code": "JP", "language": "japanese", "url_resolved": "https://nhkworld.webcdn.stream.ne.jp/www11/radiojapan/all/aac128/en.m3u8", "favicon": "", "tags": "news,public", "votes": 8200, "bitrate": 128},
        {"station_uuid": "jp-2", "name": "J-Wave 81.3", "country": "Japan", "country_code": "JP", "language": "japanese", "url_resolved": "https://mtist.as.smartstream.ne.jp/30027/livestream/playlist.m3u8", "favicon": "", "tags": "pop,j-pop", "votes": 7400, "bitrate": 128},
        {"station_uuid": "jp-3", "name": "Tokyo FM", "country": "Japan", "country_code": "JP", "language": "japanese", "url_resolved": "https://mtist.as.smartstream.ne.jp/30023/livestream/playlist.m3u8", "favicon": "", "tags": "pop,variety", "votes": 6900, "bitrate": 128},
        {"station_uuid": "jp-4", "name": "InterFM897", "country": "Japan", "country_code": "JP", "language": "english,japanese", "url_resolved": "https://mtist.as.smartstream.ne.jp/30019/livestream/playlist.m3u8", "favicon": "", "tags": "multilingual,pop", "votes": 5800, "bitrate": 128},
        {"station_uuid": "jp-5", "name": "FMcocolo765", "country": "Japan", "country_code": "JP", "language": "japanese", "url_resolved": "https://mtist.as.smartstream.ne.jp/30018/livestream/playlist.m3u8", "favicon": "", "tags": "adult contemporary", "votes": 5100, "bitrate": 128},
    ],
    "BR": [
        {"station_uuid": "br-1", "name": "Radio Nacional", "country": "Brazil", "country_code": "BR", "language": "portuguese", "url_resolved": "https://radios.ebc.com.br/nacional-am-brasilia", "favicon": "", "tags": "public,news", "votes": 7600, "bitrate": 128},
        {"station_uuid": "br-2", "name": "Radio Globo", "country": "Brazil", "country_code": "BR", "language": "portuguese", "url_resolved": "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_GLOBO_RJ.mp3", "favicon": "", "tags": "talk,news", "votes": 6900, "bitrate": 128},
        {"station_uuid": "br-3", "name": "Antena 1", "country": "Brazil", "country_code": "BR", "language": "portuguese", "url_resolved": "https://antena1.com.br/player/stream.php", "favicon": "", "tags": "pop,hits", "votes": 6200, "bitrate": 128},
        {"station_uuid": "br-4", "name": "Radio Transamérica", "country": "Brazil", "country_code": "BR", "language": "portuguese", "url_resolved": "https://playerservices.streamtheworld.com/api/livestream-redirect/TRANSAMERICA.mp3", "favicon": "", "tags": "rock", "votes": 5700, "bitrate": 128},
        {"station_uuid": "br-5", "name": "Jovem Pan", "country": "Brazil", "country_code": "BR", "language": "portuguese", "url_resolved": "https://playerservices.streamtheworld.com/api/livestream-redirect/JOVEM_PAN_AM.mp3", "favicon": "", "tags": "talk,news", "votes": 5200, "bitrate": 128},
    ],
}


def _parse_station(raw: dict) -> Station:
    """Convert raw Radio Browser API response dict into a Station schema."""
    return Station(
        station_uuid=raw["station_uuid"],
        name=raw["name"],
        country=raw["country"],
        country_code=raw["country_code"],
        language=raw.get("language", ""),
        stream_url=raw.get("url_resolved") or raw.get("url", ""),
        favicon=raw.get("favicon", ""),
        tags=[t.strip() for t in raw.get("tags", "").split(",") if t.strip()],
        votes=int(raw.get("votes", 0)),
        bitrate=int(raw.get("bitrate", 0)),
    )


async def fetch_stations(country_code: str, limit: int = 5) -> list[Station]:
    """
    Fetch top stations for a given ISO 3166-1 alpha-2 country code.
    Falls back to mock data if the Radio Browser API is unreachable.
    """
    url = f"{RADIO_BROWSER_BASE}/stations/bycountrycodeexact/{country_code.upper()}"
    params = {
        "limit": limit,
        "order": "votes",
        "reverse": "true",
        "hidebroken": "true",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params, headers=HEADERS)
            response.raise_for_status()
            raw_stations = response.json()
            return [_parse_station(s) for s in raw_stations[:limit]]
    except Exception:
        # Fall back to mock data for development
        code = country_code.upper()
        mock = MOCK_STATIONS.get(code, [])
        return [_parse_station(s) for s in mock[:limit]]
