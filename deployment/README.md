# Deployment Notes

Production deployment runs the FastAPI app with `uvicorn app.main:app`.

Recommended container flow:

```bash
cp .env.example .env
docker compose up --build
```

Set `COINMARKETCAP_API_KEY` for live OHLCV ingestion. The app remains runnable with local seed datasets when API credentials are unavailable.
