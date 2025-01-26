import os
from typing import List, Dict, Union
from alpaca.trading.client import TradingClient # type: ignore
from alpaca.trading.requests import GetAssetsRequest# type: ignore
from alpaca.trading.enums import AssetClass # type: ignore
from tabulate import tabulate # type: ignore

def get_crypto_assets(
    api_key: str = None, 
    secret_key: str = None, 
    print_assets: bool = True, 
    format: str = 'raw'
) -> Union[List[Dict], str]:
    """
    Fetch all crypto assets from Alpaca Trading API.
    
    Args:
        api_key (str, optional): Alpaca API key. Defaults to environment variable.
        secret_key (str, optional): Alpaca secret key. Defaults to environment variable.
        print_assets (bool, optional): Whether to print assets. Defaults to True.
        format (str, optional): Output format. Options: 'raw', 'table'. Defaults to 'raw'.
    
    Returns:
        List of crypto asset dictionaries or formatted table string
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
            for asset in assets
        ]
        
        # Render table
        headers = ['Symbol', 'Name', 'Status', 'Tradable', 'Marginable', 'Shortable']
        formatted_assets = tabulate(asset_data, headers=headers, tablefmt='grid')
    else:
        # Raw format
        formatted_assets = assets
    
    # Print assets if specified
    if print_assets:
        print(formatted_assets)
    
    return formatted_assets

def main():
    """
    Main function to demonstrate crypto asset retrieval
    """
    try:
        get_crypto_assets()
    except Exception as e:
        print(f"Error retrieving crypto assets: {e}")

if __name__ == '__main__':
    main()
