from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import pandas as pd
import io
import json
from datetime import datetime, timedelta
import database as db
import numpy as np

app = FastAPI(title="WiFi Demand Forecasting API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs - read from environment variables for Docker compatibility
import os
CLASSICAL_SERVICE_URL = os.getenv("CLASSICAL_SERVICE_URL", "http://localhost:8001")
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8002")
DL_SERVICE_URL = os.getenv("DL_SERVICE_URL", "http://localhost:8003")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    db.init_database()
    # Load data if database is empty
    try:
        latest = db.get_latest_date()
        if not latest:
            db.load_demand_data()
    except:
        db.load_demand_data()

class EmulateRequest(BaseModel):
    city: str
    actual_count: int
    temperature: float
    rainfall: float

@app.get("/")
def read_root():
    return {"message": "WiFi Demand Forecasting API Gateway"}

@app.get("/data/cities")
def get_cities():
    """Get list of available cities"""
    return {
        "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra"]
    }

@app.get("/data/current")
def get_current_data(city: Optional[str] = None):
    """Get latest demand data"""
    df = db.get_demand_history(city=city, limit=7)
    return {
        "data": df.to_dict(orient='records'),
        "latest_date": db.get_latest_date()
    }

@app.get("/data/history")
def get_history(city: str, days: int = 30):
    """Get historical demand data"""
    latest_date = db.get_latest_date()
    start_date = (datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=days)).strftime('%Y-%m-%d')
    
    df = db.get_demand_history(city=city, start_date=start_date, end_date=latest_date)
    df = df.sort_values('date')
    
    return {
        "city": city,
        "data": df.to_dict(orient='records'),
        "total_records": len(df)
    }

@app.post("/forecast/demand")
async def forecast_demand(city: str, model: str, horizon: int = 7):
    """Generate demand forecast for a city"""
    
    # Get historical data (last 90 days)
    latest_date = db.get_latest_date()
    start_date = (datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=90)).strftime('%Y-%m-%d')
    
    df = db.get_demand_history(city=city, start_date=start_date, end_date=latest_date)
    df = df.sort_values('date')
    
    if len(df) < 30:
        raise HTTPException(status_code=400, detail="Not enough historical data")
    
    # Prepare data for forecasting
    data_records = df.to_dict(orient='records')
    
    # Determine service based on model
    if model in ['arima', 'sarima', 'es']:
        service_url = CLASSICAL_SERVICE_URL
        service_type = 'classical'
    elif model in ['rf', 'gbm', 'svm', 'xgboost']:
        service_url = ML_SERVICE_URL
        service_type = 'ml'
    elif model in ['lstm', 'gru', 'transformer']:
        service_url = DL_SERVICE_URL
        service_type = 'dl'
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
    
    # Call forecasting service
    payload = {
        "data": data_records,
        "target_column": "request_count",
        "date_column": "date",
        "model": model,
        "horizon": horizon,
        "params": {}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{service_url}/predict", json=payload, timeout=120.0)
            response.raise_for_status()
            result = response.json()
            
            # Save forecasts to database
            forecast_date = latest_date
            for i, predicted_count in enumerate(result['forecast']):
                target_date = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=i+1)).strftime('%Y-%m-%d')
                db.save_forecast(forecast_date, target_date, city, model, int(predicted_count))
            
            # Generate future dates
            future_dates = [(datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                           for i in range(horizon)]
            
            return {
                "city": city,
                "model": model,
                "forecast_date": forecast_date,
                "forecasts": [
                    {"date": date, "predicted_count": int(count)} 
                    for date, count in zip(future_dates, result['forecast'])
                ]
            }
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

@app.post("/emulate/day")
async def emulate_day(request: EmulateRequest):
    """Emulate a new day and compare with forecasts"""
    
    # Add new day to database
    new_date = db.emulate_new_day(
        request.city,
        request.actual_count,
        request.temperature,
        request.rainfall
    )
    
    # Get forecasts for this date (if any)
    # TODO: Query forecasts table
    
    return {
        "success": True,
        "new_date": new_date,
        "city": request.city,
        "actual_count": request.actual_count,
        "message": f"Emulated new day: {new_date}"
    }

@app.get("/performance/summary")
def get_performance_summary():
    """Get model performance summary"""
    # TODO: Calculate MAE, RMSE, MAPE from forecasts vs actuals
    return {
        "models": [
            {"name": "ARIMA", "mae": 12.5, "rmse": 15.3, "mape": 8.2},
            {"name": "Random Forest", "mae": 10.2, "rmse": 13.1, "mape": 6.8},
            {"name": "LSTM", "mae": 9.8, "rmse": 12.5, "mape": 6.5}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
