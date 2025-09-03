"""
Token filtering system with configurable criteria.
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FilterSettings:
    """Configuration for token filtering."""
    min_liquidity_usd: float = 10000.0
    min_volume_h24_usd: float = 50000.0
    min_price_change_h24: float = -99.0
    max_price_change_h24: float = 1000.0
    exclude_meme_coins: bool = False
    allowed_tokens: List[str] = None
    blocked_tokens: List[str] = None
    
    def __post_init__(self):
        if self.allowed_tokens is None:
            self.allowed_tokens = []
        if self.blocked_tokens is None:
            self.blocked_tokens = []

class TokenFilter:
    """Filters tokens based on configured criteria."""
    
    def __init__(self, settings=None):
        self.settings = settings or FilterSettings()
    
    def passes_filters(self, token_data) -> bool:
        """Check if token passes all filters."""
        if token_data.liquidity_usd < self.settings.min_liquidity_usd:
            return False
        if token_data.volume_h24 < self.settings.min_volume_h24_usd:
            return False
        if (token_data.price_change_h24 < self.settings.min_price_change_h24 or 
            token_data.price_change_h24 > self.settings.max_price_change_h24):
            return False
        if self.settings.exclude_meme_coins and 'meme' in token_data.base_token_name.lower():
            return False
        if (self.settings.blocked_tokens and 
            token_data.base_token_symbol in self.settings.blocked_tokens):
            return False
        if (self.settings.allowed_tokens and 
            token_data.base_token_symbol not in self.settings.allowed_tokens):
            return False
        return True
