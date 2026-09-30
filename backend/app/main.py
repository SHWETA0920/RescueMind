from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import audio, dashboard, photo, sms

app = FastAPI(
    title="Incident Triage Copilot",
    description=(
        "Multimodal emergency call & incident triage API. Ingests audio "
        "calls, SMS texts, and scene photos; masks PII; extracts structured "
        "incident entities; and runs a deterministic urgency classifier."
    ),
    version="0.1.0",
)

def _build_origins() -> list[str]:
    raw = settings.CORS_ORIGINS
    if isinstance(raw, str):
        raw = raw.strip()
        if raw.startswith("["):
            import json
            raw = json.loads(raw)
        else:
            raw = raw.split(",")
    origins = {str(o).strip().rstrip("/") for o in raw if str(o).strip()}
    origins |= {"http://localhost:5173", "http://127.0.0.1:5173"}
    return sorted(origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(audio.router)
app.include_router(sms.router)
app.include_router(photo.router)
app.include_router(dashboard.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "mock_mode": settings.MOCK_MODE}
