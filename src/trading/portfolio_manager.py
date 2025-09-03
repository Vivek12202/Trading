"""
Portfolio manager with profit-taking rules.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Position:
    """Track a position in a token."""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    partial_sell_price: float  # 2x price for partial sell
    partial_sell_executed: bool = False
    status: str = "open"

class PortfolioManager:
    """Manages portfolio positions and risk."""
    
    def __init__(self, initial_balance: float = 1000.0, partial_sell_ratio: float = 0.5):
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.positions = {}
        self.partial_sell_ratio = partial_sell_ratio
    
    def update_position(self, symbol: str, quantity: float, price: float, order_type: str) -> bool:
        """Update portfolio after trade execution."""
        cost = abs(quantity) * price
        
        if order_type == 'buy':
            if self.cash >= cost:
                self.cash -= cost
                
                # Create new position
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    entry_time=datetime.now(),
                    partial_sell_price=price * 2.0  # 2x price for partial sell
                )
                self.positions[symbol] = position
                print(f"Bought {quantity} {symbol} at ${price:.6f}. Cash: ${self.cash:.2f}")
                return True
            else:
                print(f"Insufficient funds to buy {quantity} {symbol}")
                return False
        
        elif order_type == 'sell':
            if symbol in self.positions:
                position = self.positions[symbol]
                actual_quantity = min(quantity, position.quantity)
                self.cash += actual_quantity * price
                position.quantity -= actual_quantity
                
                if position.quantity == 0:
                    position.status = "closed"
                    print(f"Closed position in {symbol}")
                else:
                    print(f"Partially sold {actual_quantity} {symbol}")
                
                print(f"Sold {actual_quantity} {symbol} at ${price:.6f}. Cash: ${self.cash:.2f}")
                return True
            else:
                print(f"No position to sell for {symbol}")
                return False
        
        return False
    
    def check_profit_taking_opportunities(self, current_prices: dict) -> list:
        """Check for profit-taking opportunities at 2x price."""
        sell_orders = []
        
        for symbol, position in self.positions.items():
            if position.status != "open":
                continue
            
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                # Check if we should execute partial sell at 2x price
                if (not position.partial_sell_executed and 
                    current_price >= position.partial_sell_price):
                    
                    quantity_to_sell = position.quantity * self.partial_sell_ratio
                    if quantity_to_sell > 0:
                        sell_orders.append({
                            'symbol': symbol,
                            'quantity': quantity_to_sell,
                            'price': current_price
                        })
                        position.partial_sell_executed = True
                        print(f"Triggered partial sell at 2x for {symbol}")
        
        return sell_orders
