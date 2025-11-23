# WiFi Service Demand Forecasting System

Complete WiFi service demand forecasting system for Australian cities with multiple deployment options.

## Quick Start

### Option 1: Docker Compose (Recommended for Local)

```bash
docker-compose up --build
# Access: http://localhost:8080
```

### Option 2: Shell Script (Development)

```bash
./start_services.sh
# Access: http://localhost:8080
```

### Option 3: Render.com (Production)

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

```bash
# Push to GitHub
git init && git add . && git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

# Deploy on Render using render.yaml blueprint
```

## Features

- **Demand Forecasting**: Predict WiFi service requests for 6 Australian cities
- **Multiple Models**: Classical (ARIMA, SARIMA), ML (RF, XGBoost), DL (LSTM, GRU)
- **Service Engineer View**: Smart job allocation based on location and demand
- **Day Emulation**: Simulate new days and compare forecasts vs actuals
- **Light/Dark Theme**: Professional UI with theme toggle
- **Pre-loaded Data**: 2190 records (365 days × 6 cities)

## Architecture

```
Frontend (8080) → Gateway (8000) → Classical (8001)
                                  → ML (8002)
                                  → DL (8003)
```

## Documentation

- [Docker Deployment](DOCKER_DEPLOYMENT.md)
- [Render.com Deployment](RENDER_DEPLOYMENT.md)
- [Multivariate Forecasting](MULTIVARIATE_FORECASTING.md)

## Tech Stack

- **Backend**: FastAPI, Python 3.10
- **ML/DL**: scikit-learn, statsmodels, Ridge regression
- **Frontend**: FastAPI + HTML/CSS/JS, Chart.js
- **Database**: SQLite
- **Deployment**: Docker Compose, Render.com

## Deployment Options Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| Shell Script | Development | Fast, simple | Manual management |
| Docker Compose | Local/Testing | Isolated, reproducible | Requires Docker |
| Render.com | Production | Managed, scalable | Free tier has limits |

## Development

```bash
# Install dependencies for a service
cd gateway && pip install -r requirements.txt

# Run a single service
cd gateway && uvicorn main:app --port 8000
```

## License

MIT
