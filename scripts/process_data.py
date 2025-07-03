import pandas as pd
from scripts.fetch_data import fetch_data  # Adjust this based on your structure

def clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        symbol = filepath.split('/')[-1].split('_')[0]
        try:
            print(f"{filepath} not found. Fetching data for {symbol}...")
            fetch_data(symbol)
            df = pd.read_csv(filepath)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame()
    
    df = df.rename(columns={'date': 'ds', 'close': 'y'})
    df['ds'] = pd.to_datetime(df['ds'])
    df = df[['ds', 'y']].dropna()
    return df
