import os
import argparse
from dotenv import load_dotenv

# Import the function you want to make available
from src.bot.crypto_assets import get_crypto_assets

# Load environment variables
load_dotenv()

def main(function_name: str = None, **kwargs):
    """
    Main entry point for crypto trading bot.
    Dynamically calls functions based on the function name.
    
    Args:
        function_name (str): Name of the function to call
        **kwargs: Keyword arguments to pass to the function
    """
    # Dictionary mapping function names to actual functions
    available_functions = {
        'get_crypto_assets': get_crypto_assets,
        # Add more functions here as you develop them
    }
    
    # Check if the function exists
    if not function_name:
        print("Available functions:")
        for func_name in available_functions.keys():
            print(f"- {func_name}")
        return
    
    # Validate function name
    if function_name not in available_functions:
        print(f"Error: Function '{function_name}' not found.")
        print("Available functions:")
        for func_name in available_functions.keys():
            print(f"- {func_name}")
        return
    
    # Get the function
    func = available_functions[function_name]
    
    try:
        # Remove unsupported arguments for specific functions
        if function_name == 'get_crypto_assets':
            kwargs.pop('render', None)
            kwargs['print_assets'] = kwargs.get('print_assets', True)
            kwargs['format'] = kwargs.get('format', 'raw')
        
        # Call the function with provided kwargs
        result = func(**kwargs)
        return result
    except Exception as e:
        print(f"Error executing {function_name}: {e}")
        return None

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Crypto Trading Bot')
    
    # Function selection argument
    parser.add_argument('function', nargs='?', 
                        help='Function to execute')
    
    # Alpaca API credentials (optional)
    parser.add_argument('--api_key', type=str, 
                        help='Alpaca API Key', 
                        default=os.getenv('ALPACA_API_KEY'))
    parser.add_argument('--secret_key', type=str, 
                        help='Alpaca Secret Key', 
                        default=os.getenv('ALPACA_SECRET_KEY'))
    
    # Print flag for crypto assets
    parser.add_argument('--print_assets', type=bool, 
                        help='Print crypto assets', 
                        default=True)
    
    # Format flag for crypto assets
    parser.add_argument('--format', type=str, 
                        help='Output format (raw or table)', 
                        default='raw', 
                        choices=['raw', 'table'])
    
    return parser.parse_args()

if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_arguments()
    
    # Prepare kwargs for the main function
    kwargs = {
        'function_name': args.function,
        'api_key': args.api_key,
        'secret_key': args.secret_key,
        'print_assets': args.print_assets,
        'format': args.format
    }
    
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    # Call main with parsed arguments
    main(**kwargs)