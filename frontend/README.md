# Automobile Price Dashboard

Vite + React static app for Experiment 7.

## Local

```bash
cp .env.example .env
npm install
npm run dev
```

`VITE_API_URL` must point at the FastAPI server (default `http://127.0.0.1:8000`).

## Vercel

- Root directory: `frontend`
- Build: `npm run build`
- Output: `dist`
- Env: `VITE_API_URL` = public API origin
