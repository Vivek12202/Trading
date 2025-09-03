"""
Main entry point for the trading bot.
"""
from trading.main import TradingBot

def main():
    """Initialize and run the trading bot."""
    bot = TradingBot()
    bot.run()

if __name__ == "__main__":
    main()
