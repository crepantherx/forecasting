import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

DATABASE_PATH = 'forecasting.db'

def init_database():
    """Initialize the database with schema"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Demand history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demand_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            city TEXT NOT NULL,
            request_count INTEGER NOT NULL,
            temperature_c REAL,
            rainfall_mm REAL,
            day_of_week INTEGER,
            is_weekend INTEGER,
            is_holiday INTEGER,
            month INTEGER,
            population_density INTEGER,
            UNIQUE(date, city)
        )
    ''')
    
    # Forecasts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            forecast_date TEXT NOT NULL,
            target_date TEXT NOT NULL,
            city TEXT NOT NULL,
            model TEXT NOT NULL,
            predicted_count INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Model performance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            city TEXT,
            mae REAL,
            rmse REAL,
            mape REAL,
            last_updated TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def load_demand_data(csv_path='demand_data.csv'):
    """Load demand data from CSV into database"""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_csv(csv_path)
    df.to_sql('demand_history', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Loaded {len(df)} records into database")

def get_demand_history(city=None, start_date=None, end_date=None, limit=None):
    """Retrieve demand history"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = "SELECT * FROM demand_history WHERE 1=1"
    params = []
    
    if city:
        query += " AND city = ?"
        params.append(city)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    query += " ORDER BY date DESC"
    
    if limit:
        query += f" LIMIT {limit}"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def save_forecast(forecast_date, target_date, city, model, predicted_count):
    """Save a forecast"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO forecasts (forecast_date, target_date, city, model, predicted_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (forecast_date, target_date, city, model, predicted_count, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_latest_date():
    """Get the latest date in the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(date) FROM demand_history")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def emulate_new_day(city, actual_count, temperature, rainfall):
    """Add a new day of data (emulation)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get latest date
    latest_date = get_latest_date()
    new_date = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Calculate day characteristics
    dt = datetime.strptime(new_date, '%Y-%m-%d')
    day_of_week = dt.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0
    month = dt.month
    
    # Get population density for city
    cursor.execute("SELECT population_density FROM demand_history WHERE city = ? LIMIT 1", (city,))
    pop_density = cursor.fetchone()[0]
    
    # Insert new record
    cursor.execute('''
        INSERT INTO demand_history 
        (date, city, request_count, temperature_c, rainfall_mm, day_of_week, is_weekend, is_holiday, month, population_density)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    ''', (new_date, city, actual_count, temperature, rainfall, day_of_week, is_weekend, month, pop_density))
    
    conn.commit()
    conn.close()
    
    return new_date

if __name__ == '__main__':
    # Initialize and load data
    init_database()
    load_demand_data()
    print("Database initialized successfully")
    
    # Test queries
    print("\nLatest date:", get_latest_date())
    print("\nSydney last 5 days:")
    print(get_demand_history(city='Sydney', limit=5))
