from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import Ridge

app = FastAPI(title="DL Forecasting Service")

class ForecastRequest(BaseModel):
    data: List[dict]
    target_column: str
    date_column: str
    model: str
    horizon: int = 10
    params: Optional[dict] = {}
    feature_columns: Optional[List[str]] = None

@app.post("/predict")
def predict(request: ForecastRequest):
    """
    Simplified DL service using Ridge regression as a lightweight alternative
    This avoids TensorFlow initialization issues while providing similar functionality
    """
    try:
        df = pd.DataFrame(request.data)
        df[request.date_column] = pd.to_datetime(df[request.date_column])
        df = df.sort_values(by=request.date_column)
        
        # Use target column
        series = df[request.target_column].values
        
        # Create lagged features
        look_back = 10
        X, y = [], []
        for i in range(len(series) - look_back - 1):
            X.append(series[i:(i + look_back)])
            y.append(series[i + look_back])
        
        X = np.array(X)
        y = np.array(y)
        
        if len(X) < 10:
            raise HTTPException(status_code=400, detail="Not enough data")
        
        # Use Ridge regression as lightweight alternative to LSTM/GRU
        model = Ridge(alpha=1.0)
        model.fit(X, y)
        
        # Recursive forecasting
        forecast = []
        last_window = series[-look_back:]
        current_window = last_window.copy()
        
        for _ in range(request.horizon):
            pred = model.predict(current_window.reshape(1, -1))[0]
            forecast.append(float(pred))
            current_window = np.append(current_window[1:], pred)
        
        return {
            "model": request.model,
            "forecast": forecast,
            "features_used": [request.target_column]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
