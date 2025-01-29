import os
import json
import requests
import argparse
from datetime import datetime
from uuid import uuid4
import time

def fetch_crypto_bars(symbol='BTC/USD', 
                      start_date='2020-01-01', 
                      end_date='2024-01-01', 
                      timeframe='1Min'):
    """
    Fetch historical cryptocurrency bars from Alpaca API
    
    Args:
        symbol (str): Cryptocurrency symbol (default: BTC/USD)
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        timeframe (str): Bar timeframe (default: 1Min)

    Returns:
        dict: JSON response containing historical bar data
    """
    # Encode the symbol for URL
    encoded_symbol = symbol.replace('/', '%2F')
    
    # Construct the URL (removed limit parameter)
    url = f"https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols={encoded_symbol}&timeframe={timeframe}&start={start_date}&end={end_date}&sort=asc"
    
    # Headers for the request
    headers = {"accept": "application/json"}
    
    try:
        # Send GET request
        response = requests.get(url, headers=headers)
        
        # Raise an exception for bad responses
        response.raise_for_status()
        
        # Return JSON response
        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching crypto bars: {e}")
        return None

def save_bars_to_json(bars, symbol, start_date, end_date, timeframe):
    """
    Save bars to a JSON file with a date-prefixed filename
    
    Args:
        bars (list): List of bar data
        symbol (str): Cryptocurrency symbol
        start_date (str): Start date
        end_date (str): End date
        timeframe (str): Bar timeframe
    
    Returns:
        str: Path to the saved JSON file
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate filename with date prefix and unique ID
    current_date = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid4())
    filename = f"data/{current_date}_{symbol.replace('/', '_')}_{start_date}_{end_date}_{timeframe}_{unique_id}.json"
    
    # Save to JSON file
    with open(filename, 'w') as f:
        json.dump({
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "timeframe": timeframe,
            "bars": bars
        }, f, indent=2)
    
    return filename

def fetch_all_crypto_bars(symbol='BTC/USD', start_date='2020-01-01', end_date='2024-01-01', timeframe='1Min'):
    encoded_symbol = symbol.replace('/', '%2F')
    all_bars = []
    next_page_token = None
    max_retries = 5
    retry_delay = 5  # seconds

    while True:
        url = f"https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols={encoded_symbol}&timeframe={timeframe}&start={start_date}&end={end_date}&limit=10000&sort=asc"
        if next_page_token:
            url += f"&page_token={next_page_token}"
        
        headers = {"accept": "application/json"}
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                bars = data.get('bars', {}).get(symbol, [])
                all_bars.extend(bars)
                
                save_bars_to_json(bars, symbol, start_date, end_date, timeframe)
                
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    return all_bars  # Exit loop if no more pages
                
                break  # Break out of retry loop if successful
            
            except requests.RequestException as e:
                print(f"Error fetching crypto bars: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Exiting.")
                    return all_bars

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch historical cryptocurrency bars')
    parser.add_argument('--symbol', default='BTC/USD', help='Cryptocurrency symbol')
    parser.add_argument('--start', default='2020-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', default='2024-01-01', help='End date (YYYY-MM-DD)')
    parser.add_argument('--timeframe', default='1Min', help='Bar timeframe')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Fetch bars
    bars = fetch_all_crypto_bars(
        symbol=args.symbol,
        start_date=args.start,
        end_date=args.end,
        timeframe=args.timeframe
    )
    
    if bars:
        # Save bars to JSON file
        json_file = save_bars_to_json(
            bars, 
            args.symbol, 
            args.start, 
            args.end, 
            args.timeframe
        )
        
        print(f"Bars saved to: {json_file}")
        # print("First few bars:")
        
        # # Correctly access the list of bars
        # try:
        #     bars_list = bars['bars']['bars'][args.symbol]
        #     if isinstance(bars_list, list):
        #         for bar in bars_list[:5]:
        #             print(bar)
        #     else:
        #         print("No bars available or incorrect data format.")
        # except KeyError:
        #     print("No bars available or incorrect data format.")

if __name__ == "__main__":
    main() 