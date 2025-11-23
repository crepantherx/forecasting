from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

app = FastAPI(title="ML Forecasting Service")

class ForecastRequest(BaseModel):
    data: List[dict]
    target_column: str
    date_column: str
    model: str  # 'rf', 'gbm', 'svm', 'xgboost'
    horizon: int = 10
    params: Optional[dict] = {}
    feature_columns: Optional[List[str]] = None  # NEW: Allow explicit feature selection

def create_multivariate_features(df, target_col, date_col, feature_cols, lags):
    """
    Create features from:
    1. Lagged values of target
    2. All other columns (weather, geography, etc.)
    3. Time-based features (day of week, month, etc.)
    """
    df_features = df.copy()
    
    # 1. Create lagged features from target
    for lag in range(1, lags + 1):
        df_features[f'lag_{lag}'] = df_features[target_col].shift(lag)
    
    # 2. Extract time features from date column
    df_features['day_of_week'] = df_features[date_col].dt.dayofweek
    df_features['day_of_month'] = df_features[date_col].dt.day
    df_features['month'] = df_features[date_col].dt.month
    df_features['quarter'] = df_features[date_col].dt.quarter
    df_features['year'] = df_features[date_col].dt.year
    
    # 3. Include specified feature columns (weather, geography, etc.)
    # These will be used as-is if numeric, or encoded if categorical
    
    return df_features.dropna()

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
        lags = request.params.get('lags', 5)
        
        # Determine feature columns
        if request.feature_columns:
            feature_cols = request.feature_columns
        else:
            # Use all columns except date and target
            feature_cols = [c for c in df.columns if c not in [request.date_column, request.target_column]]
        
        # Create features
        df_processed = create_multivariate_features(df, request.target_column, request.date_column, feature_cols, lags)
        
        if df_processed.empty:
            raise HTTPException(status_code=400, detail="Not enough data points for the requested lag.")

        # Prepare feature columns for training
        exclude_cols = [request.date_column, request.target_column]
        
        # Encode categorical features
        df_encoded, encoders = encode_categorical_features(df_processed, exclude_cols)
        
        # Select features: lagged values + time features + additional feature columns
        feature_names = [c for c in df_encoded.columns if c.startswith('lag_') or 
                        c in ['day_of_week', 'day_of_month', 'month', 'quarter', 'year'] or
                        c in feature_cols]
        
        X = df_encoded[feature_names]
        y = df_encoded[request.target_column]
        
        # Train model
        if request.model.lower() == 'rf':
            n_estimators = request.params.get('n_estimators', 100)
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        elif request.model.lower() == 'gbm':
            model = GradientBoostingRegressor(random_state=42)
        elif request.model.lower() == 'svm':
            model = SVR()
        elif request.model.lower() == 'xgboost':
            model = XGBRegressor(random_state=42)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
            
        model.fit(X, y)
        
        # Recursive forecasting
        # For simplicity, we'll use the last known values for additional features
        # In a real scenario, you might want to forecast these too or use expected values
        last_row = df_encoded.iloc[-1]
        last_window = df[request.target_column].values[-lags:]
        forecast = []
        
        current_window = last_window.copy()
        
        # Get the last date for time feature generation
        last_date = df[request.date_column].iloc[-1]
        
        for i in range(request.horizon):
            # Create feature vector for prediction
            future_date = last_date + pd.Timedelta(days=i+1)
            
            # Build feature dict
            feature_dict = {}
            
            # Lagged features
            for lag_idx, lag in enumerate(range(lags, 0, -1)):
                feature_dict[f'lag_{lag}'] = current_window[lag_idx]
            
            # Time features
            feature_dict['day_of_week'] = future_date.dayofweek
            feature_dict['day_of_month'] = future_date.day
            feature_dict['month'] = future_date.month
            feature_dict['quarter'] = future_date.quarter
            feature_dict['year'] = future_date.year
            
            # Additional features (use last known values)
            for col in feature_cols:
                if col in df_encoded.columns:
                    feature_dict[col] = last_row[col]
            
            # Create feature array in correct order
            input_features = np.array([[feature_dict.get(fn, 0) for fn in feature_names]])
            
            pred = model.predict(input_features)[0]
            forecast.append(float(pred))
            
            # Update window
            current_window = np.append(current_window[1:], pred)
            
        return {
            "model": request.model,
            "forecast": forecast,
            "features_used": feature_names
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
