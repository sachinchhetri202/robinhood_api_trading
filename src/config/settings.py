"""Configuration settings for the Robinhood client"""

import os

class Settings:
    """Settings class for Robinhood client"""
    
    def __init__(self):
        """Initialize settings from environment variables"""
        self.API_KEY = os.getenv('API_KEY')
        self.BASE64_PRIVATE_KEY = os.getenv('BASE64_PRIVATE_KEY')
        self.ROBINHOOD_API_BASE_URL = os.getenv('ROBINHOOD_API_BASE_URL', 'https://api.robinhood.com')
    
    def validate(self) -> bool:
        """Validate required settings are present"""
        return bool(self.API_KEY and self.BASE64_PRIVATE_KEY)

# Global settings instance
settings = Settings() 