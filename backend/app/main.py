from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.trip import router as trip_router

app = FastAPI(title="Deesha Backend", version="0.1.0")

# Allow your local frontend (Live Server / Vite / React) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip_router)

@app.get("/health")
def health():
    return {"status": "ok"}
