from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, SimpleRNN
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

app = FastAPI(title="DL Forecasting Service")

class ForecastRequest(BaseModel):
    data: List[dict]
    target_column: str
    date_column: str
    model: str  # 'lstm', 'gru', 'transformer'
    horizon: int = 10
    params: Optional[dict] = {}
    feature_columns: Optional[List[str]] = None  # NEW: Allow explicit feature selection

def create_multivariate_dataset(data, look_back=1):
    """
    Create dataset for multivariate time series
    data: shape (n_samples, n_features)
    Returns X: (n_samples, look_back, n_features), y: (n_samples,)
    """
    X, Y = [], []
    for i in range(len(data) - look_back - 1):
        X.append(data[i:(i + look_back), :])
        Y.append(data[i + look_back, 0])  # Predict first column (target)
    return np.array(X), np.array(Y)

def encode_categorical_features(df, exclude_cols):
    """Encode categorical columns using LabelEncoder"""
    encoders = {}
    df_encoded = df.copy()
    
    for col in df.columns:
        if col in exclude_cols:
            continue
        if df[col].dtype == 'object' or df[col].dtype.name == 'category':
            encoders[col] = LabelEncoder()
            df_encoded[col] = encoders[col].fit_transform(df[col].astype(str))
    
    return df_encoded, encoders

@app.post("/predict")
def predict(request: ForecastRequest):
    try:
        df = pd.DataFrame(request.data)
        df[request.date_column] = pd.to_datetime(df[request.date_column])
        df = df.sort_values(by=request.date_column)
        
        # Parameters
        look_back = request.params.get('look_back', 10)
        epochs = request.params.get('epochs', 10)  # Keep low for demo speed
        batch_size = request.params.get('batch_size', 1)
        
        # Determine feature columns
        if request.feature_columns:
            feature_cols = request.feature_columns
        else:
            # Use all columns except date and target
            feature_cols = [c for c in df.columns if c not in [request.date_column, request.target_column]]
        
        # Add time-based features
        df['day_of_week'] = df[request.date_column].dt.dayofweek
        df['day_of_month'] = df[request.date_column].dt.day
        df['month'] = df[request.date_column].dt.month
        df['quarter'] = df[request.date_column].dt.quarter
        
        # Encode categorical features
        exclude_cols = [request.date_column, request.target_column]
        df_encoded, encoders = encode_categorical_features(df, exclude_cols)
        
        # Prepare feature columns: target + additional features + time features
        all_feature_cols = [request.target_column] + feature_cols + ['day_of_week', 'day_of_month', 'month', 'quarter']
        all_feature_cols = [c for c in all_feature_cols if c in df_encoded.columns]
        
        # Extract data
        data = df_encoded[all_feature_cols].values
        
        # Normalize all features
        scaler = MinMaxScaler(feature_range=(0, 1))
        data_scaled = scaler.fit_transform(data)
        
        if len(data_scaled) <= look_back:
            raise HTTPException(status_code=400, detail="Not enough data for the requested look_back period.")

        X, y = create_multivariate_dataset(data_scaled, look_back)
        
        n_features = X.shape[2]
        
        # Build Model
        model = Sequential()
        
        if request.model.lower() == 'lstm':
            model.add(LSTM(50, input_shape=(look_back, n_features)))
        elif request.model.lower() == 'gru':
            model.add(GRU(50, input_shape=(look_back, n_features)))
        elif request.model.lower() == 'transformer':
            # Simplified "Transformer" with stacked LSTM
            model.add(LSTM(100, return_sequences=True, input_shape=(look_back, n_features)))
            model.add(LSTM(50))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
            
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
        
        # Forecast
        forecast = []
        last_window = data_scaled[-look_back:]
        current_window = last_window.copy()
        
        last_date = df[request.date_column].iloc[-1]
        
        for i in range(request.horizon):
            # Prepare input
            input_data = current_window.reshape(1, look_back, n_features)
            
            # Predict
            pred_scaled = model.predict(input_data, verbose=0)[0, 0]
            
            # Create next row with predicted value and last known feature values
            future_date = last_date + pd.Timedelta(days=i+1)
            next_row = current_window[-1].copy()
            next_row[0] = pred_scaled  # Update target column
            
            # Update time features (indices depend on position in all_feature_cols)
            # Find indices of time features
            time_feature_indices = {}
            for idx, col in enumerate(all_feature_cols):
                if col == 'day_of_week':
                    time_feature_indices['day_of_week'] = idx
                elif col == 'day_of_month':
                    time_feature_indices['day_of_month'] = idx
                elif col == 'month':
                    time_feature_indices['month'] = idx
                elif col == 'quarter':
                    time_feature_indices['quarter'] = idx
            
            # Update time features with future date
            if 'day_of_week' in time_feature_indices:
                next_row[time_feature_indices['day_of_week']] = scaler.transform([[future_date.dayofweek] + [0]*(n_features-1)])[0, 0]
            if 'day_of_month' in time_feature_indices:
                next_row[time_feature_indices['day_of_month']] = scaler.transform([[future_date.day] + [0]*(n_features-1)])[0, 0]
            if 'month' in time_feature_indices:
                next_row[time_feature_indices['month']] = scaler.transform([[future_date.month] + [0]*(n_features-1)])[0, 0]
            if 'quarter' in time_feature_indices:
                next_row[time_feature_indices['quarter']] = scaler.transform([[future_date.quarter] + [0]*(n_features-1)])[0, 0]
            
            # Shift window
            current_window = np.vstack([current_window[1:], next_row])
            
            # Store forecast (inverse transform only the target column)
            forecast_value = scaler.inverse_transform([next_row])[0, 0]
            forecast.append(float(forecast_value))
        
        return {
            "model": request.model,
            "forecast": forecast,
            "features_used": all_feature_cols
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
