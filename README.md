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
source quantenv/bin/activate  # On Windows use: quantenv\Scriptsctivate
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

### Available Functions
- `get_crypto_assets`: Retrieve crypto assets from Alpaca
- `render_crypto_assets`: Display crypto assets in a tabular format

### Command Line Examples

#### List Available Functions
```bash
python index.py
```

#### Get Crypto Assets
```bash
# Using .env credentials
python index.py get_crypto_assets

# With custom API keys
python index.py get_crypto_assets --api_key YOUR_API_KEY --secret_key YOUR_SECRET_KEY
```

#### Render Crypto Assets
```bash
# Default rendering
python index.py render_crypto_assets

# Disable rendering
python index.py render_crypto_assets --render False
```

## Development Roadmap
- [ ] Implement trading strategies
- [ ] Add more crypto asset management functions
- [ ] Create comprehensive test suite
- [ ] Implement logging and error tracking

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