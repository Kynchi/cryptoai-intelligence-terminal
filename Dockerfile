FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/package.json
COPY frontend/tsconfig.json frontend/vite.config.ts frontend/tailwind.config.ts frontend/postcss.config.cjs frontend/
RUN cd frontend && npm install
COPY frontend frontend
RUN cd frontend && npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CRYPTO_FORECAST_CONFIG=configs/config.json

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl git libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend-builder /frontend/frontend/dist /app/frontend/dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
