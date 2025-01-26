import os
from typing import List, Dict
from alpaca.trading.client import TradingClient # type: ignore
from alpaca.trading.requests import GetAssetsRequest# type: ignore
from alpaca.trading.enums import AssetClass # type: ignore
from tabulate import tabulate # type: ignore

def get_crypto_assets(api_key: str = None, secret_key: str = None) -> List[Dict]:
    """
    Fetch all crypto assets from Alpaca Trading API.
    
    Args:
        api_key (str, optional): Alpaca API key. Defaults to environment variable.
        secret_key (str, optional): Alpaca secret key. Defaults to environment variable.
    
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
    
    return assets

def render_crypto_assets(assets: List[Dict] = None):
    """
    Render crypto assets in a tabular format.
    
    Args:
        assets (List[Dict], optional): List of crypto assets. If None, fetches assets.
    """
    if assets is None:
        assets = get_crypto_assets()
    
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
        for asset in assets
    ]
    
    # Render table
    headers = ['Symbol', 'Name', 'Status', 'Tradable', 'Marginable', 'Shortable']
    print(tabulate(asset_data, headers=headers, tablefmt='grid'))

def main():
    """
    Main function to demonstrate crypto asset retrieval and rendering
    """
    try:
        render_crypto_assets()
    except Exception as e:
        print(f"Error retrieving crypto assets: {e}")

if __name__ == '__main__':
    main()
