import os
import time
import threading
import numpy as np
import pandas as pd
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Import our market data functions
from src.bot.market_data import (
    get_persistent_crypto_bars,
    get_persistent_crypto_orderbooks,
    CryptoWebSocketClient
)

@dataclass
class StrategySignal:
    """
    Represents a trading signal with comprehensive information
    """
    symbol: str
    timestamp: datetime
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float = 0.0
    price: Optional[float] = None
    order_book_imbalance: Optional[float] = None
    volume_trend: Optional[float] = None
    volatility: Optional[float] = None
    additional_info: Dict = field(default_factory=dict)

class CryptoQuantitativeStrategy:
    def __init__(
        self, 
        symbols: List[str] = ['BTC/USD', 'ETH/USD'],
        bar_interval: int = 1,
        orderbook_interval: int = 1,
        risk_tolerance: float = 0.02,
        take_profit_ratio: float = 0.05,
        stop_loss_ratio: float = 0.03
    ):
        """
        Initialize the quantitative trading strategy
        
        Args:
            symbols (List[str]): Crypto symbols to trade
            bar_interval (int): Interval for bar data updates
            orderbook_interval (int): Interval for order book updates
            risk_tolerance (float): Maximum portfolio risk per trade
            take_profit_ratio (float): Take profit percentage
            stop_loss_ratio (float): Stop loss percentage
        """
        self.symbols = symbols
        self.bar_interval = bar_interval
        self.orderbook_interval = orderbook_interval
        
        # Risk management parameters
        self.risk_tolerance = risk_tolerance
        self.take_profit_ratio = take_profit_ratio
        self.stop_loss_ratio = stop_loss_ratio
        
        # Data storage
        self.bars_data = {}
        self.orderbooks_data = {}
        self.trade_data = {}
        
        # Strategy parameters
        self.short_window = 10
        self.long_window = 30
        
        # Signal tracking
        self.current_signals = {}
        
        # Threading events
        self.stop_event = threading.Event()
        
    def _calculate_order_book_imbalance(self, orderbook: Dict) -> float:
        """
        Calculate order book imbalance
        
        Args:
            orderbook (Dict): Order book data
        
        Returns:
            float: Order book imbalance (-1 to 1)
        """
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            total_bid_volume = sum(float(bid[1]) for bid in bids)
            total_ask_volume = sum(float(ask[1]) for ask in asks)
            
            # Normalized imbalance
            imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
            return imbalance
        except Exception:
            return 0.0
    
    def _calculate_volatility(self, bars: List[Dict]) -> float:
        """
        Calculate price volatility
        
        Args:
            bars (List[Dict]): Price bars
        
        Returns:
            float: Volatility measure
        """
        try:
            prices = [float(bar.get('c', 0)) for bar in bars]
            returns = np.diff(prices) / prices[:-1]
            return np.std(returns)
        except Exception:
            return 0.0
    
    def _generate_signal(self, symbol: str) -> Optional[StrategySignal]:
        """
        Generate trading signal based on multiple factors
        
        Args:
            symbol (str): Crypto symbol
        
        Returns:
            Optional[StrategySignal]: Trading signal
        """
        try:
            # Ensure we have data for the symbol
            if (symbol not in self.bars_data or 
                symbol not in self.orderbooks_data or 
                len(self.bars_data[symbol]) < self.long_window):
                return None
            
            # Extract recent data
            bars = self.bars_data[symbol][-self.long_window:]
            orderbook = self.orderbooks_data[symbol]
            
            # Calculate indicators
            current_price = float(bars[-1].get('c', 0))
            order_book_imbalance = self._calculate_order_book_imbalance(orderbook)
            volatility = self._calculate_volatility(bars)
            
            # Moving average crossover
            short_ma = np.mean([float(bar.get('c', 0)) for bar in bars[-self.short_window:]])
            long_ma = np.mean([float(bar.get('c', 0)) for bar in bars])
            
            # Signal generation logic
            confidence = 0.0
            signal_type = 'HOLD'
            
            # Bullish signals
            if (short_ma > long_ma and 
                order_book_imbalance > 0.3 and 
                volatility < 0.02):
                signal_type = 'BUY'
                confidence = min(0.8 + order_book_imbalance, 1.0)
            
            # Bearish signals
            elif (short_ma < long_ma and 
                  order_book_imbalance < -0.3 and 
                  volatility > 0.05):
                signal_type = 'SELL'
                confidence = min(0.8 - order_book_imbalance, 1.0)
            
            return StrategySignal(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                order_book_imbalance=order_book_imbalance,
                volatility=volatility
            )
        
        except Exception as e:
            print(f"Signal generation error for {symbol}: {e}")
            return None
    
    def _process_bars(self, bars: Dict):
        """
        Process incoming bar data
        
        Args:
            bars (Dict): Bar data for multiple symbols
        """
        for symbol, bar_data in bars.items():
            if symbol not in self.bars_data:
                self.bars_data[symbol] = []
            
            # Keep only last 100 bars
            self.bars_data[symbol].append(bar_data)
            if len(self.bars_data[symbol]) > 100:
                self.bars_data[symbol] = self.bars_data[symbol][-100:]
            
            # Generate signal
            signal = self._generate_signal(symbol)
            if signal:
                self.current_signals[symbol] = signal
                print(f"Signal for {symbol}: {signal}")
    
    def _process_orderbooks(self, orderbooks: Dict):
        """
        Process incoming order book data
        
        Args:
            orderbooks (Dict): Order book data for multiple symbols
        """
        for symbol, orderbook_data in orderbooks.items():
            self.orderbooks_data[symbol] = orderbook_data
    
    def _process_trades(self, trade_data: Dict):
        """
        Process incoming trade data
        
        Args:
            trade_data (Dict): Trade data
        """
        # Additional trade processing can be added here
        pass
    
    def start_strategy(self):
        """
        Start the quantitative trading strategy
        """
        print("Starting Quantitative Crypto Trading Strategy...")
        
        # Start bar data streaming
        bars_stop_event = get_persistent_crypto_bars(
            symbols=self.symbols,
            interval=self.bar_interval,
            on_update=self._process_bars
        )
        
        # Start order book streaming
        orderbooks_stop_event = get_persistent_crypto_orderbooks(
            symbols=self.symbols,
            interval=self.orderbook_interval,
            on_update=self._process_orderbooks
        )
        
        # Start WebSocket trade streaming
        ws_client = CryptoWebSocketClient(symbols=self.symbols)
        ws_client.start(on_message_callback=self._process_trades)
        
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping strategy...")
        finally:
            bars_stop_event.set()
            orderbooks_stop_event.set()
            ws_client.stop()
    
    def stop_strategy(self):
        """
        Stop the quantitative trading strategy
        """
        self.stop_event.set()

def main():
    """
    Main function to demonstrate the strategy
    """
    strategy = CryptoQuantitativeStrategy(
        symbols=['BTC/USD', 'ETH/USD'],
        bar_interval=1,
        orderbook_interval=1
    )
    
    try:
        strategy.start_strategy()
    except KeyboardInterrupt:
        strategy.stop_strategy()

if __name__ == '__main__':
    main() 