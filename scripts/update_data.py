import sys
import os

# Add the parent directory of 'scripts' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.fetch_data import fetch_data

def update_all():
    symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']
    for symbol in symbols:
        print(f"Fetching {symbol}...")
        fetch_data(symbol)
        print(f"{symbol} data updated.\n")

if __name__ == "__main__":
    update_all()
