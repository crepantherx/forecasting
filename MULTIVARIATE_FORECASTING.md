# Multivariate Forecasting Enhancement

## Overview
The ML and DL services have been enhanced to support **multivariate time series forecasting**. This means they can now use **all available columns** in your dataset (weather, geography, topography, etc.) to make better predictions.

## What Changed

### ML Service (Random Forest, GBM, SVM, XGBoost)
**New Features:**
1. **Automatic Feature Extraction**: Uses all columns except date and target
2. **Time-Based Features**: Automatically creates day_of_week, day_of_month, month, quarter, year
3. **Categorical Encoding**: Automatically encodes text/categorical columns
4. **Lagged Features**: Still creates lagged values of the target variable
5. **Returns Features Used**: Response now includes `features_used` to show which features were used

**Example Request:**
```json
{
  "data": [
    {"date": "2024-01-01", "region": "Sydney", "weather": "Sunny", "temperature": 28, "eta": 5.2},
    {"date": "2024-01-02", "region": "Melbourne", "weather": "Rainy", "temperature": 18, "eta": 7.8}
  ],
  "target_column": "eta",
  "date_column": "date",
  "model": "rf",
  "horizon": 10
}
```

The model will automatically use: `region`, `weather`, `temperature` + time features + lagged ETA values.

### DL Service (LSTM, GRU, Transformer)
**New Features:**
1. **Multivariate Input**: Accepts multiple feature columns
2. **Time-Based Features**: Same as ML service
3. **Categorical Encoding**: Same as ML service
4. **Proper Sequence Handling**: Maintains temporal dependencies across all features
5. **Returns Features Used**: Response now includes `features_used`

## Use Case: WiFi Service ETA Prediction

For your **Australia WiFi service request** use case, the enhanced models can now use:

### Input Features
- **Geographic**: Latitude, Longitude, Region, Area Type (Urban/Suburban/Rural)
- **Weather**: Temperature, Rainfall, Weather Condition
- **Topography**: Elevation, Terrain Type
- **Service Details**: Request Type, Population Density, Infrastructure Quality
- **Temporal**: Day of week, Month, Quarter (auto-generated)

### How It Works
1. Upload CSV with all these columns
2. Select `RequestDate` as date column
3. Select `ActualETA` as target column
4. Choose ML or DL model
5. The model automatically:
   - Encodes categorical features (e.g., "Sydney" → 0, "Melbourne" → 1)
   - Creates time features
   - Uses ALL features to predict ETA
   - Generates forecasts for future service requests

## Example Dataset Structure

```csv
RequestDate,Region,Latitude,Longitude,Weather,Temperature,Topography,PopulationDensity,ActualETA
2024-01-01,Sydney,-33.8688,151.2093,Sunny,28,Urban,High,5.2
2024-01-02,Melbourne,-37.8136,144.9631,Rainy,18,Suburban,Medium,7.8
2024-01-03,Brisbane,-27.4698,153.0251,Cloudy,25,Urban,High,6.1
...
```

## Benefits

1. **Better Predictions**: Uses all available information, not just past ETA values
2. **Captures Patterns**: Understands how weather, location, etc. affect ETA
3. **Automatic Processing**: No manual feature engineering needed
4. **Handles Categorical Data**: Automatically encodes text columns
5. **Time-Aware**: Understands seasonal and weekly patterns

## Frontend Support

The frontend already supports this! Simply:
1. Upload your multi-column CSV
2. Select date and target columns
3. All other columns are automatically used as features
4. Generate forecast

## Technical Details

### ML Service
- **Feature Engineering**: Combines lagged values + additional columns + time features
- **Encoding**: LabelEncoder for categorical columns
- **Forecasting**: Uses last known values for additional features during prediction

### DL Service
- **Architecture**: Multivariate LSTM/GRU/Transformer
- **Input Shape**: (samples, look_back, n_features)
- **Normalization**: MinMaxScaler applied to all features
- **Forecasting**: Updates time features for future dates, uses last known values for other features

## Limitations

- **Future Feature Values**: For features like weather, the model uses the last known values during forecasting
- **In production**, you might want to:
  - Forecast weather separately
  - Use expected/average values for future dates
  - Integrate with external APIs for real-time data

## Next Steps

The system is ready to use! Upload your WiFi service dataset and start forecasting ETAs with all available features.
