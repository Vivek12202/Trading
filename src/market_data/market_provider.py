"""
Market data provider using DexScreener API.
"""
import requests
import json
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TokenData:
    """Data class for token information."""
    pair_address: str
    base_token_name: str
    base_token_symbol: str
    price_usd: float
    volume_h24: float
    liquidity_usd: float
    price_change_h24: float

class MarketDataProvider:
    """Provides market data from DexScreener."""
    
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
    
    def fetch_pair_data(self, pair_address: str) -> Optional[TokenData]:
        """Fetch data for a specific token pair."""
        try:
            url = f"{self.base_url}/pairs/{pair_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'pair' in 
                    pair = data['pair']
                    return TokenData(
                        pair_address=pair['pairAddress'],
                        base_token_name=pair['baseToken']['name'],
                        base_token_symbol=pair['baseToken']['symbol'],
                        price_usd=float(pair['priceUsd']),
                        volume_h24=float(pair['volumeH24']),
                        liquidity_usd=float(pair['liquidity']['usd']),
                        price_change_h24=float(pair['priceChange']['h24'])
                    )
            return None
        except Exception as e:
            print(f"Error fetching pair  {e}")
            return None
