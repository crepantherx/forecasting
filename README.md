# WiFi Service Demand Forecasting System

Complete WiFi service demand forecasting system for Australian cities with Docker deployment support.

## Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:8080
# API Gateway: http://localhost:8000
```

### Option 2: Shell Script (Development)

```bash
# Start all services locally
./start_services.sh
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

- [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Multivariate Forecasting](MULTIVARIATE_FORECASTING.md)

## Tech Stack

- **Backend**: FastAPI, Python 3.10
- **ML/DL**: scikit-learn, statsmodels, Ridge regression
- **Frontend**: FastAPI + HTML/CSS/JS, Chart.js
- **Database**: SQLite
- **Deployment**: Docker Compose

## Development

```bash
# Install dependencies for a service
cd gateway && pip install -r requirements.txt

# Run a single service
cd gateway && uvicorn main:app --port 8000
```

## License

MIT
