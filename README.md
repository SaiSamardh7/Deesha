@@ -1,2 +1,40 @@
# Deesha
an AI based travel planner

# Deesha — Trip Planner MVP

Deesha is a lightweight trip planning MVP that generates a basic itinerary from user inputs (start city, destination, number of days, group size, and preferences).

This repo contains:
- A simple frontend (HTML/CSS/JS)
- A FastAPI backend that returns itinerary JSON

## Features (MVP)
- Multi-step trip setup UI
- Backend API:
  - `GET /health` — health check
  - `POST /plan-trip` — returns an itinerary response

## Tech Stack
- Frontend: HTML/CSS/JavaScript
- Backend: Python (FastAPI + Uvicorn)

---

## How to Run the Project (Beginner Friendly)

### Run Backend (macOS / Linux)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
