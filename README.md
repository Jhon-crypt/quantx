# QuantX Crypto Trading Bot

## Project Overview
QuantX is a flexible crypto trading bot built with Python, leveraging the Alpaca Trading API for asset management and trading strategies.

## Project Structure
```
quantx/
│
├── src/
│   └── bot/
│       └── market_data.py     # Core market data functions
│
├── tests/                       # Future test directory
├── data/                        # Data storage
├── config/                      # Configuration files
├── index.py                     # Main entry point
└── requirements.txt             # Project dependencies
```

## Prerequisites
- Python 3.8+
- Alpaca Trading Account
- API Keys from Alpaca

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/quantx.git
cd quantx
```

### 2. Create Virtual Environment
```bash
python3 -m venv quantenv
source quantenv/bin/activate  # On Windows use: quantenv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Credentials
Create a `.env` file in the project root:
```
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

## Market Data Functions

### 1. Crypto Assets Retrieval

#### Command Line Usage
```bash
# Default (prints raw assets)
python index.py get_crypto_assets

# With tabular format
python index.py get_crypto_assets --format table

# Disable printing
python index.py get_crypto_assets --print_assets False
```

#### Python Usage
```python
from src.bot.market_data import get_crypto_assets

# Get all tradable crypto assets
assets = get_crypto_assets()

# Get assets in table format
assets_table = get_crypto_assets(format='table', print_assets=False)
```

### 2. Persistent Crypto Bar Fetching

#### Command Line Usage
```bash
# Default (fetch bars for all tradable assets every second)
python index.py --bars

# Specify symbols and custom interval
python index.py --bars --symbols BTC/USD ETH/USD --interval 2

# Disable printing
python index.py --bars --print_bars False
```

#### Python Usage
```python
from src.bot.market_data import get_persistent_crypto_bars
import time

# Optional callback to process bar updates
def process_bars(bars):
    for symbol, bar in bars.items():
        print(f"{symbol} - Close: {bar.get('c', 'N/A')}")

# Start persistent bar fetching
stop_event = get_persistent_crypto_bars(
    symbols=['BTC/USD', 'ETH/USD'],  # Optional: specify symbols
    interval=1,  # Fetch every second (default)
    on_update=process_bars
)

# Keep main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Stop bar fetching on interrupt
    stop_event.set()
```

### 3. WebSocket Streaming

#### Python Usage
```python
from src.bot.market_data import CryptoWebSocketClient

# Create WebSocket client
ws_client = CryptoWebSocketClient()

# Callback to process incoming trade data
def process_trade(trade_data):
    print("Trade Update:", trade_data)
    # Add your trading logic here

# Start WebSocket streaming with callback
ws_client.start(on_message_callback=process_trade)

# Keep main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Stop WebSocket on interrupt
    ws_client.stop()
```

### 4. Crypto Data Manager

```python
from src.bot.market_data import CryptoDataManager

# Initialize data manager with custom refresh interval
data_manager = CryptoDataManager(refresh_interval=30)

# Optional callback for periodic updates
def on_data_update(bars):
    print("Updated Bars:", bars)

# Start periodic data refresh
data_manager.start_periodic_refresh(
    symbols=['BTC/USD', 'ETH/USD'], 
    callback=on_data_update
)

# Get latest cached bars
latest_bars = data_manager.get_latest_bars()

# Stop periodic refresh when done
data_manager.stop_periodic_refresh()
```

### 5. Persistent Crypto Order Books

#### Command Line Usage
```bash
# Default (fetch order books for all tradable assets every second)
python index.py --orderbooks

# Specify symbols and custom interval
python index.py --orderbooks --orderbook_symbols BTC/USD ETH/USD --orderbook_interval 2

# Disable printing
python index.py --orderbooks --print_orderbooks False
```

#### Python Usage
```python
from src.bot.market_data import get_persistent_crypto_orderbooks
import time

# Optional callback to process order book updates
def process_orderbooks(orderbooks):
    for symbol, orderbook in orderbooks.items():
        print(f"{symbol} Order Book:")
        print(f"Bids: {orderbook.get('bids', 'N/A')}")
        print(f"Asks: {orderbook.get('asks', 'N/A')}")

# Start persistent order book fetching
stop_event = get_persistent_crypto_orderbooks(
    symbols=['BTC/USD', 'ETH/USD'],  # Optional: specify symbols
    interval=1,  # Fetch every second (default)
    on_update=process_orderbooks
)

# Keep main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Stop order book fetching on interrupt
    stop_event.set()
```

## Advanced Features
- Ultra-fast 1-second crypto market data updates
- Persistent real-time bar data streaming
- Real-time order book tracking
- Flexible bar and order book fetching with custom parameters
- Configurable fetch intervals
- Automatic symbol discovery
- Callback-based data processing
- Background data fetching
- WebSocket trade streaming

## Development Roadmap
- [ ] Implement advanced trading strategies
- [ ] Add more crypto data analysis tools
- [ ] Create comprehensive test suite
- [ ] Implement advanced logging and error tracking

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/quantx](https://github.com/yourusername/quantx)