import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Australian cities with their characteristics
CITIES = {
    'Sydney': {'lat': -33.8688, 'lon': 151.2093, 'pop_density': 2058, 'base_demand': 150},
    'Melbourne': {'lat': -37.8136, 'lon': 144.9631, 'pop_density': 1566, 'base_demand': 130},
    'Brisbane': {'lat': -27.4698, 'lon': 153.0251, 'pop_density': 1031, 'base_demand': 100},
    'Perth': {'lat': -31.9505, 'lon': 115.8605, 'pop_density': 330, 'base_demand': 80},
    'Adelaide': {'lat': -34.9285, 'lon': 138.6007, 'pop_density': 407, 'base_demand': 70},
    'Canberra': {'lat': -35.2809, 'lon': 149.1300, 'pop_density': 171, 'base_demand': 50}
}

# Australian public holidays 2024
HOLIDAYS = [
    '2024-01-01', '2024-01-26', '2024-03-29', '2024-04-01', '2024-04-25',
    '2024-06-10', '2024-12-25', '2024-12-26'
]

def generate_demand_data(start_date='2024-01-01', days=365):
    """Generate synthetic WiFi service demand data for Australian cities"""
    
    data = []
    start = datetime.strptime(start_date, '%Y-%m-%d')
    
    for day_offset in range(days):
        current_date = start + timedelta(days=day_offset)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Day characteristics
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
        is_weekend = day_of_week >= 5
        is_holiday = date_str in HOLIDAYS
        month = current_date.month
        day_of_year = current_date.timetuple().tm_yday
        
        # Seasonal factor (higher demand in summer/spring for installations)
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        for city, info in CITIES.items():
            # Base demand
            base = info['base_demand']
            
            # Weekly pattern (lower on weekends)
            weekly_factor = 0.7 if is_weekend else 1.0
            
            # Holiday effect (much lower demand)
            holiday_factor = 0.4 if is_holiday else 1.0
            
            # Random variation
            random_factor = np.random.normal(1.0, 0.15)
            
            # Weather simulation (simplified)
            # Summer: higher temp, less rain
            # Winter: lower temp, more rain
            if month in [12, 1, 2]:  # Summer
                temp = np.random.normal(28, 4)
                rain = np.random.exponential(2) if random.random() < 0.3 else 0
            elif month in [6, 7, 8]:  # Winter
                temp = np.random.normal(15, 3)
                rain = np.random.exponential(5) if random.random() < 0.5 else 0
            else:  # Spring/Autumn
                temp = np.random.normal(22, 3)
                rain = np.random.exponential(3) if random.random() < 0.4 else 0
            
            # Weather impact (rain reduces demand slightly)
            weather_factor = 0.9 if rain > 10 else 1.0
            
            # Calculate final demand
            demand = base * seasonal_factor * weekly_factor * holiday_factor * weather_factor * random_factor
            demand = max(int(demand), 10)  # Minimum 10 requests per day
            
            # Add some special events (random spikes)
            if random.random() < 0.05:  # 5% chance of special event
                demand = int(demand * np.random.uniform(1.5, 2.5))
            
            data.append({
                'date': date_str,
                'city': city,
                'request_count': demand,
                'temperature_c': round(temp, 1),
                'rainfall_mm': round(rain, 1),
                'day_of_week': day_of_week,
                'is_weekend': int(is_weekend),
                'is_holiday': int(is_holiday),
                'month': month,
                'population_density': info['pop_density']
            })
    
    return pd.DataFrame(data)

if __name__ == '__main__':
    # Generate data
    df = generate_demand_data(days=365)
    
    # Save to CSV
    df.to_csv('demand_data.csv', index=False)
    print(f"Generated {len(df)} records for {len(CITIES)} cities over 365 days")
    print(f"\nSample data:")
    print(df.head(10))
    print(f"\nSummary statistics:")
    print(df.groupby('city')['request_count'].describe())
