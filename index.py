import os
from dotenv import load_dotenv
from src.bot.crypto_assets import get_crypto_assets, render_crypto_assets

# Load environment variables
load_dotenv()

def main(
    api_key: str = None, 
    secret_key: str = None, 
    render: bool = True
):
    """
    Main entry point for crypto trading bot.
    
    Args:
        api_key (str, optional): Alpaca API key
        secret_key (str, optional): Alpaca secret key
        render (bool, optional): Whether to render assets. Defaults to True.
    
    Returns:
        List of crypto assets
    """
    # Fetch crypto assets
    try:
        assets = get_crypto_assets(api_key, secret_key)
        
        # Render if specified
        if render:
            render_crypto_assets(assets)
        
        return assets
    
    except Exception as e:
        print(f"Error in main function: {e}")
        return []

if __name__ == '__main__':
    # Example usage with environment variables
    main()