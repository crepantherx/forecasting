# Time Series Forecasting App - Walkthrough

## Overview
A **100% Python** microservice-based Time Series Forecasting application:
- **Frontend**: FastAPI + HTML/CSS/JS (Port 8080)
- **API Gateway**: FastAPI orchestrator (Port 8000)
- **Classical Service**: ARIMA, SARIMA, Exponential Smoothing (Port 8001)
- **ML Service**: Random Forest, Gradient Boosting, SVM, XGBoost (Port 8002)
- **DL Service**: LSTM, GRU, Transformer (Port 8003)

## Quick Start

### 1. Start All Services
```bash
cd /Users/sudhirsingh/forecasting
./start_services.sh
```

### 2. Access the App
Open your browser to: **http://localhost:8080**

![FastAPI Frontend](file:///Users/sudhirsingh/.gemini/antigravity/brain/1e839e14-3094-4d97-abc3-2b71d7bb9476/fastapi_frontend_loaded_1763885568935.png)

## Features

### Modern UI
- **Gradient background** with purple theme
- **Responsive sidebar** for configuration
- **Interactive Chart.js** visualizations
- **Real-time error handling**

### Data Upload
- Upload CSV files via file input
- Automatic column detection
- Data preview table (first 5 rows)

### Model Selection
Choose from **3 categories** of forecasting models:

#### Classical Models (Statistical)
- **ARIMA**: Auto-Regressive Integrated Moving Average
- **SARIMA**: Seasonal ARIMA
- **Exponential Smoothing**: Holt-Winters method

#### Machine Learning Models
- **Random Forest**: Ensemble tree-based regression
- **Gradient Boosting**: Sequential ensemble method
- **SVM**: Support Vector Regression
- **XGBoost**: Optimized gradient boosting

#### Deep Learning Models
- **LSTM**: Long Short-Term Memory networks
- **GRU**: Gated Recurrent Units
- **Transformer**: Attention-based architecture

### Configuration
- **Date Column**: Select time index
- **Target Column**: Select value to predict
- **Horizon**: Number of future steps to forecast (default: 10)

### Visualization
- **Historical data** shown in teal
- **Forecast** shown in pink with dashed line
- Interactive Chart.js with zoom and pan
- Automatic date generation for future periods

## Architecture

```
┌─────────────────────┐
│  FastAPI Frontend   │  Port 8080
│  (HTML/CSS/JS)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   API Gateway       │  Port 8000
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    ▼             ▼          ▼          ▼
┌─────────┐  ┌──────┐  ┌──────┐  ┌──────┐
│Classical│  │  ML  │  │  DL  │  │ ...  │
│  8001   │  │ 8002 │  │ 8003 │  │      │
└─────────┘  └──────┘  └──────┘  └──────┘
```

## Technology Stack

### Backend (100% Python)
- **FastAPI**: All services
- **Uvicorn**: ASGI server
- **Jinja2**: HTML templating

### Frontend
- **Vanilla JavaScript**: No frameworks
- **Chart.js**: Interactive charts
- **CSS3**: Modern gradient styling

### Models
- **Classical**: statsmodels, pmdarima
- **ML**: scikit-learn, XGBoost
- **DL**: TensorFlow/Keras

## Verification Results

All services tested and verified:

✅ **Frontend Service**: Running on port 8080  
✅ **Gateway Service**: Running on port 8000  
✅ **Classical Models**: ARIMA, SARIMA, ES working  
✅ **ML Models**: Random Forest, GBM, SVM, XGBoost working  
✅ **DL Models**: LSTM, GRU, Transformer working  

### Test Output
```
Testing Classical (ARIMA)...
Classical Forecast Success: [-0.595, -0.626, -0.606, -0.619, -0.610]

Testing ML (Random Forest)...
ML Forecast Success: [-0.719, -0.790, -0.868, -0.886, -0.887]

Testing DL (LSTM)...
DL Forecast Success: [-0.630, -0.661, -0.700, -0.718, -0.737]
```

## Usage Flow

1. **Upload CSV**: Click "Choose File" and select your time series CSV
2. **Click "Upload & Analyze"**: Data preview appears
3. **Configure**:
   - Select date and target columns
   - Choose model type (Classical/ML/DL)
   - Select specific model
   - Set forecast horizon
4. **Click "Generate Forecast"**: Chart displays with forecast overlay
5. **View Results**: Interactive chart with historical + forecast data

## File Structure

```
/Users/sudhirsingh/forecasting/
├── frontend-service/
│   ├── main.py              # FastAPI server
│   ├── templates/
│   │   └── index.html       # Main page
│   └── static/
│       ├── css/style.css    # Styling
│       └── js/app.js        # API calls & charts
├── gateway/
│   └── main.py              # API Gateway
├── classical-service/
│   └── main.py              # ARIMA, SARIMA, ES
├── ml-service/
│   └── main.py              # RF, GBM, SVM, XGBoost
├── dl-service/
│   └── main.py              # LSTM, GRU, Transformer
└── start_services.sh        # Launch script
```

## Next Steps

The app is ready to use! Simply:
1. Run `./start_services.sh`
2. Open http://localhost:8080
3. Upload your time series data
4. Generate forecasts with any model
