# Automobile Price Prediction — Experiments 6 & 7

Portfolio project: a scikit-learn Random Forest price model served with **FastAPI**, packaged in **Docker**, and explored through a **Vercel-ready dashboard** (SHAP, metrics, drift, Responsible AI).

## Project layout

```
ADS/
  main.py                 # FastAPI app
  Dockerfile              # Exp 6 image
  docker-compose.yml
  requirements.txt
  Responsible_AI.md       # Exp 7 checklist
  models/best_automobile_price_model.pkl
  api/                    # REST routes
  services/               # predict, SHAP, metrics, drift
  data/                   # UCI reference set (generated)
  frontend/               # Vite + React dashboard (Vercel)
```

## Experiment 6 — Containerization & API

### Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/prepare_reference_data.py
uvicorn main:app --reload --port 8000
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Sample JSON POST

```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict ^
  -H "Content-Type: application/json" ^
  -d @sample_request.json
```

### Docker

```bash
docker build -t automobile-price-api .
docker run --rm -p 8000:8000 automobile-price-api
```

Or `docker compose up --build`.

### API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Model loaded, log size |
| POST | `/api/v1/predict` | Price prediction |
| POST | `/api/v1/explain` | SHAP contributions |
| GET | `/api/v1/metrics` | MAE, RMSE, R², residual plots data |
| GET | `/api/v1/drift` | PSI vs UCI reference |
| GET | `/api/v1/insights` | Global SHAP + importances |
| GET | `/api/v1/schema` | Form fields for the dashboard |
| GET | `/api/v1/sample` | Example payload |

## Experiment 7 — Dashboard & Responsible AI

The UI lives in `frontend/` so Vercel can deploy that folder as a static app.

```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

### Deploy frontend on Vercel

1. Push this repository.
2. New Vercel project → set **Root Directory** to `frontend`.
3. Framework: Vite (auto-detected). Build command `npm run build`, output `dist`.
4. Environment variable `VITE_API_URL` = public URL of the FastAPI service (Render, Railway, Azure, etc.).
5. The API must allow CORS (already `allow_origins=["*"]` for this lab).

`frontend/vercel.json` rewrites all routes to `index.html` for client-side navigation.

Responsible AI checklist: [Responsible_AI.md](./Responsible_AI.md).
