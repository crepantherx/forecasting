from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pmdarima as pm

app = FastAPI(title="Classical Forecasting Service")

class ForecastRequest(BaseModel):
    data: List[dict]  # List of records e.g. [{'date': '...', 'value': 10}, ...]
    target_column: str
    date_column: str
    model: str  # 'arima', 'sarima', 'es'
    horizon: int = 10
    params: Optional[dict] = {}

@app.post("/predict")
def predict(request: ForecastRequest):
    try:
        df = pd.DataFrame(request.data)
        df[request.date_column] = pd.to_datetime(df[request.date_column])
        df = df.sort_values(by=request.date_column)
        series = df[request.target_column].values
        
        forecast = []
        
        if request.model.lower() == 'arima':
            # Simple auto-arima or fixed order
            order = request.params.get('order', (1, 1, 1))
            model = ARIMA(series, order=order)
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=request.horizon)
            
        elif request.model.lower() == 'sarima':
            order = request.params.get('order', (1, 1, 1))
            seasonal_order = request.params.get('seasonal_order', (1, 1, 1, 12))
            model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
            model_fit = model.fit(disp=False)
            forecast = model_fit.forecast(steps=request.horizon)
            
        elif request.model.lower() == 'es':
            # Exponential Smoothing
            trend = request.params.get('trend', 'add')
            seasonal = request.params.get('seasonal', 'add')
            seasonal_periods = request.params.get('seasonal_periods', 12)
            model = ExponentialSmoothing(series, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
            model_fit = model.fit()
            forecast = model_fit.forecast(request.horizon)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
        
        return {
            "model": request.model,
            "forecast": forecast.tolist()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
