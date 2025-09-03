"""
Trading strategy implementation.
"""
import pandas as pd
from dataclasses import dataclass
from typing import Any

@dataclass
class Signal:
    """Trading signal."""
    signal_type: str  # 'buy', 'sell', 'hold'
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float

class SMACrossoverStrategy:
    """SMA crossover trading strategy."""
    
    def __init__(self, fast_period: int = 10, slow_period: int = 20):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signal(self,  pd.DataFrame, current_price: float) -> Signal:
        """Generate trading signal based on SMA crossover."""
        if len(data) < self.slow_period:
            return Signal('hold', 0.0, None, None, None)
        
        # Calculate SMAs
        data_copy = data.copy()
        data_copy['fast_sma'] = data_copy['close'].rolling(self.fast_period).mean()
        data_copy['slow_sma'] = data_copy['close'].rolling(self.slow_period).mean()
        
        # Get the last two periods
        recent = data_copy.tail(2)
        
        # Check for crossover
        prev_fast = recent['fast_sma'].iloc[-2]
        curr_fast = recent['fast_sma'].iloc[-1]
        prev_slow = recent['slow_sma'].iloc[-2]
        curr_slow = recent['slow_sma'].iloc[-1]
        
        # Calculate confidence
        sma_ratio = curr_fast / curr_slow
        confidence = min(abs(sma_ratio - 1.0) * 10, 1.0)
        
        # Generate signal
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            # Golden cross - buy signal
            return Signal(
                signal_type='buy',
                confidence=confidence,
                entry_price=current_price,
                stop_loss=current_price * 0.95,
                take_profit=current_price * 1.10
            )
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            # Death cross - sell signal
            return Signal(
                signal_type='sell',
                confidence=confidence,
                entry_price=current_price,
                stop_loss=current_price * 1.05,
                take_profit=current_price * 0.90
            )
        else:
            return Signal('hold', 0.0, None, None, None)
