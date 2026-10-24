from fastapi import FastAPI
from sqlalchemy import text

from app.db import SessionLocal
from app.routers.auth import router as auth_router

app = FastAPI(
    title="SynapseAI API",
    version="0.2.0",
)

app.include_router(auth_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def readiness_check() -> dict[str, str]:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))

    return {"status": "ok", "database": "connected"}
