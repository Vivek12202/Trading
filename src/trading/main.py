"""
Main trading bot class.
"""
import time
from datetime import datetime, timedelta
from src.market_data.market_provider import MarketDataProvider
from src.filters.token_filter import TokenFilter, FilterSettings
from src.security.secure_storage import SecureStorage
from src.trading.strategy import SMACrossoverStrategy
from src.trading.portfolio_manager import PortfolioManager
from src.trading.transaction_executor import TransactionExecutor
from src.analysis.bubblemaps_api import BubblemapsAPI

class TradingBot:
    """Main trading bot class."""
    
    def __init__(self):
        self.is_running = False
        self.active_symbols = []
        self.symbol_to_address = {}
        
        # Initialize components
        self.secure_storage = SecureStorage()
        self.market_provider = MarketDataProvider()
        self.token_filter = TokenFilter()
        self.signal_generator = SMACrossoverStrategy()
        self.portfolio_manager = PortfolioManager()
        self.bubblemaps_api = BubblemapsAPI()
        
        # Initialize secure storage
        password = input("Enter secure storage password: ")
        if not self.secure_storage.initialize_storage(password):
            raise RuntimeError("Failed to initialize secure storage")
        
        print("Trading bot initialized")
    
    def add_symbol(self, symbol: str, pair_address: str):
        """Add a symbol to monitor."""
        self.active_symbols.append(symbol)
        self.symbol_to_address[symbol] = pair_address
        print(f"Added symbol {symbol}")
    
    def run_once(self):
        """Run one iteration of the bot."""
        # Update prices
        current_prices = {}
        for symbol in self.active_symbols:
            if symbol in self.symbol_to_address:
                token_data = self.market_provider.fetch_pair_data(
                    self.symbol_to_address[symbol]
                )
                if token_data:
                    current_prices[symbol] = token_data.price_usd
        
        # Check profit-taking opportunities
        profit_taking_orders = self.portfolio_manager.check_profit_taking_opportunities(
            current_prices
        )
        
        # Initialize transaction executor
        wallet_address = self.secure_storage.retrieve_secret("wallet_address")
        private_key = self.secure_storage.retrieve_secret("private_key")
        transaction_executor = TransactionExecutor(private_key, wallet_address)
        
        # Execute profit-taking sells
        for order in profit_taking_orders:
            result = transaction_executor.execute_sell(
                self.symbol_to_address[order['symbol']], 
                order['quantity']
            )
            if result.success:
                self.portfolio_manager.update_position(
                    order['symbol'],
                    order['quantity'],
                    order['price'],
                    'sell'
                )
        
        # Generate signals and execute trades
        for symbol in self.active_symbols:
            if symbol not in current_prices:
                continue
            
            # Get token address from pair data
            pair_data = self.market_provider.fetch_pair_data(self.symbol_to_address[symbol])
            if not pair_data:
                continue
            
            token_address = pair_data.base_token_address
            
            # Check rug pull risk
            risk = self.bubblemaps_api.check_rug_pull(token_address)
            if risk and risk.risk_level == "critical":
                print(f"Skipping {symbol} due to critical risk level")
                continue
            
            # Generate signal
            signal = self.signal_generator.generate_signal(
                None,  # In a real implementation, you'd fetch historical data
                current_prices[symbol]
            )
            
            # Execute trades based on signals
            if signal.signal_type == 'buy' and signal.confidence > 0.3:
                # In a real implementation, calculate position size based on risk
                result = transaction_executor.execute_buy(
                    self.symbol_to_address[symbol],
                    0.1  # Amount in SOL
                )
                if result.success:
                    self.portfolio_manager.update_position(
                        symbol,
                        100,  # Quantity (this would be calculated)
                        signal.entry_price,
                        'buy'
                    )
        
        # Print portfolio value
        total_value = self.portfolio_manager.cash
        for symbol, position in self.portfolio_manager.positions.items():
            if symbol in current_prices:
                total_value += position.quantity * current_prices[symbol]
        
        print(f"Portfolio value: ${total_value:.2f}")
    
    def run(self, duration_hours: float = 24, check_interval_minutes: int = 5):
        """Run the bot continuously."""
        self.is_running = True
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        print(f"Starting bot for {duration_hours} hours...")
        
        while self.is_running and datetime.now() < end_time:
            try:
                self.run_once()
                time.sleep(check_interval_minutes * 60)
            except KeyboardInterrupt:
                print("Bot stopped by user")
                self.is_running = False
            except Exception as e:
                print(f"Error in bot loop: {e}")
                time.sleep(60)
        
        self.is_running = False
        print("Bot stopped")
