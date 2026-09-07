# EcoSort Backend

FastAPI backend for the EcoSort waste classification system. Wraps the
ML team's ConvNeXt-Tiny model (`ml/Brain.py`) behind a REST API, logs
every classification to a database, and exposes stats/history for a
dashboard.

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLAlchemy ORM — SQLite for local dev, Neon (Postgres) planned for later
- **ML:** PyTorch / TorchVision (ConvNeXt-Tiny), wrapped via `app/services/inference.py`

## Setup

\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
\`\`\`

Place the trained model checkpoint at the path set in `.env`
(default: `ml/outputs/ecosort_convnext_tiny_best.pt`).

## Run

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs

---

## API Endpoints

Base URL prefix for all endpoints below (except `/health`): `/api/v1`

### `GET /health`

Basic liveness check.

**Response `200`**
\`\`\`json
{ "status": "ok" }
\`\`\`

---

### `POST /api/v1/classify`

Upload an image, run it through the ML model, log the result, and
return the classification.

**Request:** `multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | image file | yes | JPEG, PNG, or WEBP only |

**Response `200`**
\`\`\`json
{
  "id": 1,
  "label": "recyclable",
  "confidence": 0.8234,
  "should_sort": true,
  "created_at": "2026-09-07T12:34:56.789Z"
}
\`\`\`

| Field | Meaning |
|---|---|
| `label` | One of `biodegradable`, `non_biodegradable`, `recyclable` |
| `confidence` | Model's confidence score, 0–1 |
| `should_sort` | `true` if `confidence >= CONFIDENCE_THRESHOLD` (default 0.70), else `false` |

**Response `400`** — bad or missing file
\`\`\`json
{ "detail": "Unsupported file type 'text/plain'. Use JPEG, PNG, or WEBP." }
\`\`\`

---

### `GET /api/v1/history`

List past classifications, newest first.

**Query params**

| Param | Type | Default | Notes |
|---|---|---|---|
| `limit` | int | 20 | 1–100 |
| `offset` | int | 0 | for pagination |

**Response `200`**
\`\`\`json
[
  {
    "id": 1,
    "label": "recyclable",
    "confidence": 0.8234,
    "should_sort": true,
    "created_at": "2026-09-07T12:34:56.789Z"
  }
]
\`\`\`

---

### `GET /api/v1/stats`

Aggregate stats across all logged classifications — for dashboard charts.

**Response `200`**
\`\`\`json
{
  "total": 12,
  "by_category": {
    "biodegradable": 5,
    "non_biodegradable": 3,
    "recyclable": 4
  },
  "average_confidence": 0.8017
}
\`\`\`

---

## Project Structure

\`\`\`
ecosort-backend/
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── config.py                # settings (paths, thresholds, DB URL)
│   ├── database.py              # SQLAlchemy engine/session
│   ├── models/classification.py # DB table definition
│   ├── schemas/classification.py# API request/response shapes
│   ├── api/v1/                  # route handlers
│   └── services/inference.py    # wraps ml/Brain.py for predictions
├── ml/                           # ML team's training + inference code
│   ├── Brain.py
│   ├── camera_test.py
│   └── outputs/                 # trained checkpoints (gitignored)
├── requirements.txt
├── .env.example
└── README.md
\`\`\`

## Notes

- Model checkpoints (`*.pt`) and datasets (`data/`) are gitignored —
  too large for GitHub. Share via Drive/other means with the team.
- No image storage yet (`image_path` column exists but unused) —
  decide with team if the dashboard needs a photo gallery later.
- No hardware/servo integration yet — this backend only classifies
  and logs; physical sorting action is out of scope for now.