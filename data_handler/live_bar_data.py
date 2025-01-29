import requests
import time

url = "https://data.alpaca.markets/v1beta3/crypto/us/latest/bars"

# Specify the symbol you want to fetch
params = {
    "symbols": "BTC/USD"  # You can add more symbols separated by commas
}

# Include the API key in the headers for authentication
headers = {
    "accept": "application/json",
    
}

def fetch_latest_bars():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")

def main():
    try:
        while True:
            fetch_latest_bars()
            time.sleep(1)  # Wait for 1 second before fetching again
    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    main()
