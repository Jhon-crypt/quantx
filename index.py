import os
import argparse
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import the functions you want to make available
from src.bot.market_data import (
    get_crypto_assets, 
    get_persistent_crypto_bars,
    get_persistent_crypto_orderbooks
)

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
        'get_persistent_crypto_bars': get_persistent_crypto_bars,
        'get_persistent_crypto_orderbooks': get_persistent_crypto_orderbooks,
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
        
        if function_name == 'get_persistent_crypto_bars':
            # Remove unsupported arguments
            kwargs.pop('render', None)
            kwargs.pop('print_assets', None)
            kwargs.pop('format', None)
        
        # Call the function with provided kwargs
        result = func(**kwargs)
        
        # For persistent bars, keep the main thread running
        if function_name == 'get_persistent_crypto_bars':
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                result.set()  # Stop the bar fetching
        
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
    
    # Crypto Assets function arguments
    parser.add_argument('--print_assets', type=bool, 
                        help='Print crypto assets', 
                        default=True)
    parser.add_argument('--format', type=str, 
                        help='Output format (raw or table)', 
                        default='raw', 
                        choices=['raw', 'table'])
    
    # Crypto Bars specific arguments
    parser.add_argument('--bars', action='store_true',
                        help='Fetch crypto bars')
    parser.add_argument('--symbols', type=str, nargs='+',
                        help='Crypto symbols to retrieve bars for (e.g., BTC/USD ETH/USD)')
    parser.add_argument('--timeframe', type=str, 
                        help='Timeframe for bars', 
                        choices=['minute', 'hour', 'day'], 
                        default='minute')
    parser.add_argument('--start', type=str, 
                        help='Start date for bars (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, 
                        help='End date for bars (YYYY-MM-DD)')
    
    # Persistent Bars arguments
    parser.add_argument('--interval', type=int, 
                        help='Interval between bar fetches (seconds)', 
                        default=1)
    parser.add_argument('--print_bars', type=bool, 
                        help='Print crypto bars', 
                        default=True)
    
    # Orderbooks specific arguments
    parser.add_argument('--orderbooks', action='store_true',
                        help='Fetch crypto order books')
    parser.add_argument('--orderbook_symbols', type=str, nargs='+',
                        help='Crypto symbols to retrieve order books for (e.g., BTC/USD ETH/USD)')
    parser.add_argument('--orderbook_interval', type=int, 
                        help='Interval between order book fetches (seconds)', 
                        default=1)
    parser.add_argument('--print_orderbooks', type=bool, 
                        help='Print crypto order books', 
                        default=True)
    
    return parser.parse_args()

def main_cli():
    """
    Command-line interface entry point
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Prepare kwargs for the main function
    kwargs = {
        'function_name': args.function,
        'print_assets': args.print_assets,
        'format': args.format,
    }
    
    # Handle bar-specific arguments
    if args.bars or args.function == 'get_persistent_crypto_bars':
        kwargs.update({
            'function_name': 'get_persistent_crypto_bars',
            'symbols': args.symbols,
            'interval': args.interval,
            'print_bars': args.print_bars
        })
    
    # Handle orderbooks-specific arguments
    if args.orderbooks or args.function == 'get_persistent_crypto_orderbooks':
        kwargs.update({
            'function_name': 'get_persistent_crypto_orderbooks',
            'symbols': args.orderbook_symbols,
            'interval': args.orderbook_interval,
            'print_orderbooks': args.print_orderbooks
        })
    
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    # Call main with parsed arguments
    main(**kwargs)

if __name__ == '__main__':
    main_cli()