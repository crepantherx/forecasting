# WiFi Service Demand Forecasting - Docker Deployment

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start all services:**
```bash
docker-compose up --build
```

2. **Access the application:**
- Frontend: http://localhost:8080
- API Gateway: http://localhost:8000

3. **Stop all services:**
```bash
docker-compose down
```

### Using the Shell Script (Development)

```bash
./start_services.sh
```

## Docker Commands

### Build all images:
```bash
docker-compose build
```

### Start in detached mode:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f
```

### Restart a specific service:
```bash
docker-compose restart gateway
```

### Stop and remove containers:
```bash
docker-compose down
```

## Services

- **Gateway** (Port 8000): API Gateway and data management
- **Classical** (Port 8001): ARIMA, SARIMA, Exponential Smoothing
- **ML** (Port 8002): Random Forest, XGBoost, GBM, SVM
- **DL** (Port 8003): LSTM, GRU, Transformer
- **Frontend** (Port 8080): Web interface

## Architecture

```
┌─────────────┐
│  Frontend   │ :8080
│  (FastAPI)  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Gateway   │ :8000
│  (FastAPI)  │
└──────┬──────┘
       │
   ┌───┴────┬─────────┬─────────┐
   │        │         │         │
┌──▼──┐ ┌──▼──┐  ┌──▼──┐  ┌───▼───┐
│Class│ │ ML  │  │ DL  │  │ Data  │
│:8001│ │:8002│  │:8003│  │SQLite │
└─────┘ └─────┘  └─────┘  └───────┘
```

## Production Deployment

For production, consider:
- Using environment variables for configuration
- Adding health checks
- Implementing logging and monitoring
- Using a reverse proxy (nginx)
- Setting up SSL/TLS certificates
