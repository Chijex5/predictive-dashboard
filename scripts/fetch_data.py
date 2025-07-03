from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from utils.config import API_KEY

def fetch_data(symbol='AAPL'):
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    data, _ = ts.get_daily(symbol=symbol, outputsize='full')
    
    data = data.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    })
    data.to_csv(f'data/raw/{symbol}_daily.csv')
    print(f"Saved {symbol} data.")
