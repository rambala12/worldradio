from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import stations
from app.database import init_db

app = FastAPI(
    title="World Radio API",
    description="Browse and stream radio stations from around the world.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this down when deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(stations.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
