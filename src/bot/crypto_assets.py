import os
import requests
import time
import threading
import json
import websocket
from typing import List, Dict, Union, Callable
from alpaca.trading.client import TradingClient # type: ignore
from alpaca.trading.requests import GetAssetsRequest# type: ignore
from alpaca.trading.enums import AssetClass # type: ignore
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from tabulate import tabulate # type: ignore
import asyncio
import logging
from datetime import datetime, timedelta
import pandas as pd

class CryptoDataManager:
    def __init__(self, refresh_interval: int = 60):
        """
        Initialize Crypto Data Manager
        
        Args:
            refresh_interval (int, optional): Interval to refresh data in seconds. Defaults to 60.
        """
        self.latest_bars = {}
        self.refresh_interval = refresh_interval
        self.stop_event = threading.Event()
        self.refresh_thread = None
    
    def _fetch_bars(self, symbols: List[str] = None) -> Dict:
        """
        Fetch latest bars for given symbols
        
        Args:
            symbols (List[str], optional): List of crypto symbols
        
        Returns:
            Dictionary of latest bars
        """
        # If no symbols provided, get tradable crypto assets
        if symbols is None:
            assets = get_crypto_assets(print_assets=False)
            # Convert asset objects to symbol strings
            symbols = [asset.symbol for asset in assets]
        
        # Encode symbols for URL
        symbols_param = ','.join(symbols)
        encoded_symbols = symbols_param.replace('/', '%2F')
        
        # Construct URL
        url = f"https://data.alpaca.markets/v1beta3/crypto/us/latest/bars?symbols={encoded_symbols}"
        
        # Get API key from environment
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            raise ValueError("Alpaca API key and secret key must be provided")
        
        # Set headers
        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        
        try:
            # Make the request
            response = requests.get(url, headers=headers)
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse JSON response
            bars_data = response.json()
            
            return bars_data
        
        except requests.RequestException as e:
            print(f"Error retrieving crypto bars: {e}")
            return {}
    
    def start_periodic_refresh(
        self, 
        symbols: List[str] = None, 
        callback: Callable[[Dict], None] = None
    ):
        """
        Start periodic data refresh in a background thread
        
        Args:
            symbols (List[str], optional): Symbols to refresh
            callback (Callable, optional): Function to call with updated data
        """
        def refresh_loop():
            while not self.stop_event.is_set():
                try:
                    # Fetch latest bars
                    self.latest_bars = self._fetch_bars(symbols)
                    
                    # Call callback if provided
                    if callback:
                        callback(self.latest_bars)
                    
                    # Wait for next refresh
                    self.stop_event.wait(self.refresh_interval)
                except Exception as e:
                    print(f"Error in periodic refresh: {e}")
                    break
        
        # Stop any existing thread
        self.stop_periodic_refresh()
        
        # Start new refresh thread
        self.refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def stop_periodic_refresh(self):
        """
        Stop the periodic refresh thread
        """
        if self.refresh_thread:
            self.stop_event.set()
            self.refresh_thread.join()
            self.stop_event.clear()
    
    def get_latest_bars(self) -> Dict:
        """
        Get the latest cached bars
        
        Returns:
            Dictionary of latest bars
        """
        return self.latest_bars

class CryptoWebSocketClient:
    def __init__(
        self, 
        api_key: str = None, 
        secret_key: str = None, 
        symbols: List[str] = None
    ):
        """
        Initialize WebSocket client for crypto data streaming
        
        Args:
            api_key (str, optional): Alpaca API key
            secret_key (str, optional): Alpaca secret key
            symbols (List[str], optional): Crypto symbols to stream
        """
        # Use environment variables if keys are not provided
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API key and secret key must be provided")
        
        # Get symbols if not provided
        if symbols is None:
            assets = get_crypto_assets(print_assets=False)
            symbols = [asset.symbol for asset in assets]
        
        self.symbols = symbols
        self.websocket = None
        self.is_running = False
        self.on_message_callback = None
        self.stream_thread = None
        self.reconnect_interval = 5  # seconds between reconnection attempts
    
    def _on_message(self, ws, message):
        """
        Handle incoming WebSocket messages
        
        Args:
            ws (websocket.WebSocketApp): WebSocket connection
            message (str): Received message
        """
        try:
            data = json.loads(message)
            
            # Filter for trade messages
            if isinstance(data, list):
                for item in data:
                    if item.get('T') == 't':  # Trade message
                        if self.on_message_callback:
                            self.on_message_callback(item)
                        else:
                            print("Trade Update:", item)
        except json.JSONDecodeError:
            print("Error decoding message:", message)
    
    def _on_error(self, ws, error):
        """
        Handle WebSocket errors
        
        Args:
            ws (websocket.WebSocketApp): WebSocket connection
            error (Exception): Error that occurred
        """
        print(f"WebSocket Error: {error}")
        self.is_running = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """
        Handle WebSocket connection closure
        
        Args:
            ws (websocket.WebSocketApp): WebSocket connection
            close_status_code (int): Status code for closure
            close_msg (str): Closure message
        """
        print("WebSocket connection closed")
        self.is_running = False
        
        # Attempt to reconnect
        if self.stream_thread and not self.stream_thread.is_alive():
            print("Attempting to reconnect...")
            time.sleep(self.reconnect_interval)
            self.start(self.on_message_callback)
    
    def _on_open(self, ws):
        """
        Handle WebSocket connection opening
        
        Args:
            ws (websocket.WebSocketApp): WebSocket connection
        """
        print("WebSocket connection opened")
        self.is_running = True
        
        # Authenticate
        auth_message = {
            "action": "auth",
            "key": self.api_key,
            "secret": self.secret_key
        }
        ws.send(json.dumps(auth_message))
        
        # Subscribe to crypto trades
        subscribe_message = {
            "action": "subscribe",
            "trades": self.symbols
        }
        ws.send(json.dumps(subscribe_message))
    
    def start(self, on_message_callback: Callable[[Dict], None] = None):
        """
        Start WebSocket streaming
        
        Args:
            on_message_callback (Callable, optional): Function to handle incoming messages
        """
        # Set message callback
        self.on_message_callback = on_message_callback
        
        # WebSocket URL for crypto trades
        websocket_url = "wss://stream.data.alpaca.markets/v2/iex"
        
        # Create WebSocket connection
        self.websocket = websocket.WebSocketApp(
            websocket_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # Run WebSocket in a separate thread
        self.stream_thread = threading.Thread(
            target=self.websocket.run_forever, 
            daemon=True
        )
        self.stream_thread.start()
    
    def stop(self):
        """
        Stop WebSocket streaming
        """
        if self.websocket:
            self.websocket.close()
        
        if self.stream_thread:
            self.stream_thread.join()
        
        self.is_running = False
        print("WebSocket streaming stopped")

def get_crypto_assets(
    api_key: str = None, 
    secret_key: str = None, 
    print_assets: bool = True, 
    format: str = 'raw'
) -> List[Dict]:
    """
    Fetch all crypto assets from Alpaca Trading API.
    
    Args:
        api_key (str, optional): Alpaca API key. Defaults to environment variable.
        secret_key (str, optional): Alpaca secret key. Defaults to environment variable.
        print_assets (bool, optional): Whether to print assets. Defaults to True.
        format (str, optional): Output format. Options: 'raw', 'table'. Defaults to 'raw'.
    
    Returns:
        List of crypto asset dictionaries
    """
    # Use environment variables if keys are not provided
    api_key = api_key or os.getenv('ALPACA_API_KEY')
    secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        raise ValueError("Alpaca API key and secret key must be provided")
    
    # Initialize Trading Client
    trading_client = TradingClient(api_key, secret_key)
    
    # Search for crypto assets
    search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO)
    
    # Get all crypto assets
    assets = trading_client.get_all_assets(search_params)
    
    # Filter tradable crypto assets
    tradable_assets = [asset for asset in assets if asset.tradable]
    
    # Format output based on specified format
    if format == 'table':
        # Prepare data for tabulation
        asset_data = [
            [
                asset.symbol, 
                asset.name, 
                asset.status, 
                asset.tradable, 
                asset.marginable, 
                asset.shortable
            ] 
            for asset in tradable_assets
        ]
        
        # Render table
        headers = ['Symbol', 'Name', 'Status', 'Tradable', 'Marginable', 'Shortable']
        formatted_assets = tabulate(asset_data, headers=headers, tablefmt='grid')
        
        # Print assets if specified
        if print_assets:
            print(formatted_assets)
    else:
        # Print assets if specified
        if print_assets:
            print(tradable_assets)
    
    return tradable_assets

def get_persistent_crypto_bars(
    symbols: List[str] = None, 
    interval: int = 1,  # Changed to 1 second for faster updates
    on_update: Callable[[Dict], None] = None,
    print_bars: bool = True
):
    """
    Continuously fetch real-time bars for specified crypto symbols.
    
    Args:
        symbols (List[str], optional): List of crypto symbols. 
            Defaults to all tradable symbols from get_crypto_assets.
        interval (int, optional): Interval between bar fetches in seconds. 
            Defaults to 1 second for rapid crypto market updates.
        on_update (Callable, optional): Callback function for each bar update.
        print_bars (bool, optional): Whether to print bars. Defaults to True.
    """
    # Import here to avoid circular import
    from .crypto_assets import get_crypto_assets
    
    # If no symbols provided, get tradable crypto assets
    if symbols is None:
        assets = get_crypto_assets(print_assets=False)
        symbols = [asset.symbol for asset in assets]
    
    # Stop event to control the thread
    stop_event = threading.Event()
    
    def fetch_bars():
        """
        Internal function to fetch bars continuously
        """
        while not stop_event.is_set():
            try:
                # Encode symbols for URL
                symbols_param = ','.join(symbols)
                encoded_symbols = symbols_param.replace('/', '%2F')
                
                # Construct URL
                url = f"https://data.alpaca.markets/v1beta3/crypto/us/latest/bars?symbols={encoded_symbols}"
                
                # Get API key from environment
                api_key = os.getenv('ALPACA_API_KEY')
                secret_key = os.getenv('ALPACA_SECRET_KEY')
                
                if not api_key or not secret_key:
                    raise ValueError("Alpaca API key and secret key must be provided")
                
                # Set headers
                headers = {
                    "accept": "application/json",
                    "APCA-API-KEY-ID": api_key,
                    "APCA-API-SECRET-KEY": secret_key
                }
                
                # Make the request
                response = requests.get(url, headers=headers)
                
                # Check for successful response
                response.raise_for_status()
                
                # Parse JSON response
                bars_data = response.json()
                
                # Print bars if specified
                if print_bars:
                    print(f"Bar Update at {time.strftime('%Y-%m-%d %H:%M:%S')}:")
                    print(bars_data)
                
                # Call user-defined callback if provided
                if on_update:
                    on_update(bars_data)
                
                # Wait for next interval
                stop_event.wait(interval)
            
            except requests.RequestException as e:
                print(f"Error retrieving crypto bars: {e}")
                # Wait before retrying
                stop_event.wait(interval)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
    
    # Create and start the thread
    fetch_thread = threading.Thread(target=fetch_bars, daemon=True)
    fetch_thread.start()
    
    # Return the stop event to allow external control
    return stop_event

def main():
    """
    Demonstrate persistent bar fetching
    """
    # Optional callback to process bar updates
    def process_bars(bars):
        for symbol, bar in bars.items():
            print(f"{symbol} - Close: {bar.get('c', 'N/A')}")
    
    try:
        # Start persistent bar fetching
        stop_event = get_persistent_crypto_bars(
            symbols=['BTC/USD', 'ETH/USD'],  # Optional: specify symbols
            interval=10,  # Fetch every 10 seconds
            on_update=process_bars
        )
        
        # Keep main thread running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        # Stop bar fetching on interrupt
        stop_event.set()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
