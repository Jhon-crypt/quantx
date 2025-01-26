# QuantX Crypto Trading Bot

## Project Overview
QuantX is a flexible crypto trading bot built with Python, leveraging the Alpaca Trading API for asset management and trading strategies.

## Project Structure
```
quantx/
│
├── src/
│   └── bot/
│       └── crypto_assets.py     # Core crypto asset functions
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

## Usage

### Crypto Bar Fetching

#### Fetch Bars from Command Line
```bash
# Fetch bars for all tradable assets (default: minute timeframe)
python index.py --bars

# Specify symbols
python index.py --bars --symbols BTC/USD ETH/USD

# Change timeframe
python index.py --bars --timeframe hour

# Specify date range
python index.py --bars --start 2023-01-01 --end 2023-12-31

# Customize interval and printing
python index.py --bars --symbols BTC/USD --interval 10 --print_bars False
```

#### Persistent Bar Fetching
```bash
# Default (fetch bars for all tradable assets every 5 seconds)
python index.py

# Specify symbols and interval
python index.py --symbols BTC/USD ETH/USD --interval 10

# Disable printing
python index.py --print_bars False
```

#### Python Usage
```python
from src.bot.crypto_assets import get_persistent_crypto_bars
import time

# Optional callback to process bar updates
def process_bars(bars):
    for symbol, bar in bars.items():
        print(f"{symbol} - Close: {bar.get('c', 'N/A')}")

# Start persistent bar fetching
stop_event = get_persistent_crypto_bars(
    symbols=['BTC/USD', 'ETH/USD'],  # Optional: specify symbols
    interval=10,  # Fetch every 10 seconds
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

### Other Crypto Asset Functions

#### Get Crypto Assets
```bash
# Default (prints raw assets)
python index.py get_crypto_assets

# With tabular format
python index.py get_crypto_assets --format table

# Disable printing
python index.py get_crypto_assets --print_assets False
```

### WebSocket Streaming

#### Real-Time Trade Updates
```python
from src.bot.crypto_assets import CryptoWebSocketClient

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

## Advanced Features
- Persistent real-time bar data streaming
- Flexible bar fetching with custom parameters
- Configurable fetch intervals
- Automatic symbol discovery
- Callback-based bar processing
- Background data fetching

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