# Automobile Price Prediction API

FastAPI and React application for automobile price prediction. The backend packages a trained scikit-learn model in Docker, and the frontend provides a Vite dashboard.

## Requirements

- Python 3.11 or Docker Desktop
- Node.js and npm
- Git Bash on Windows, if using Git Bash commands

## Run the Backend with Docker

Start Docker Desktop, then run these commands from the repository root:

```bash
cd backend
docker compose up --build
```

The API will be available at:

- API: http://127.0.0.1:8000
- Swagger documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

To stop the container, press `Ctrl+C`.

## Build and Run the Docker Image

```bash
cd backend
docker build -t automobile-price-api:latest .
docker run --rm -p 8000:8000 automobile-price-api:latest
```

## Pull and Run from Docker Hub

```bash
docker pull skii4a/automobile-price-api:latest
docker run --rm -p 8000:8000 skii4a/automobile-price-api:latest
```

To publish the image first:

```bash
docker login
docker tag automobile-price-api:latest skii4a/automobile-price-api:latest
docker push skii4a/automobile-price-api:latest
```

## Test the Prediction API

With the backend running, use the sample request:

```bash
cd backend
curl -X POST http://127.0.0.1:8000/api/v1/predict \
	-H "Content-Type: application/json" \
	-d @sample_request.json
```

The response contains `success`, `predicted_price`, `currency`, and the processed input data.

Example response format:

```json
{
	"success": true,
	"predicted_price": 15800.0,
	"currency": "USD"
}
```

The exact prediction depends on the input and trained model.

## Run the Frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually http://localhost:5173. The frontend uses `frontend/.env` to connect to the backend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Checks API and model status |
| POST | `/api/v1/predict` | Predicts automobile price |
| POST | `/api/v1/explain` | Returns prediction explanation |
| GET | `/api/v1/metrics` | Returns model metrics |
| GET | `/api/v1/drift` | Returns data drift information |
| GET | `/api/v1/insights` | Returns model insights |
| GET | `/api/v1/schema` | Returns form field information |
| GET | `/api/v1/sample` | Returns an example request |

## Project Files

```text
backend/     FastAPI application, model, Dockerfile, and API routes
frontend/    React and Vite dashboard
data/        Dataset files
```
