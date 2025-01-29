import requests
import time

# URL for fetching the latest order book
orderbook_url = "https://data.alpaca.markets/v1beta3/crypto/us/latest/orderbooks"

# Specify the symbol you want to fetch
params = {
    "symbols": "BTC/USD"  # You can add more symbols separated by commas
}

# Include the API key in the headers for authentication
headers = {
    "accept": "application/json",
}

def fetch_latest_orderbook():
    response = requests.get(orderbook_url, headers=headers, params=params)
    if response.status_code == 200:
        print("Latest Order Book:", response.json())
    else:
        print(f"Error fetching order book: {response.status_code} - {response.text}")

def main():
    try:
        while True:
            fetch_latest_orderbook()
            time.sleep(1)  # Wait for 1 second before fetching again
    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    main()