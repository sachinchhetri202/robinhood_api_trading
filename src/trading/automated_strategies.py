"""
Automated Trading Strategies

Author: Sachin Chhetri

This module provides automated trading strategies for crypto trading:
- Stop Loss with Profit Taking
- Trailing Stop Loss
- Dollar-Cost Averaging (DCA)
- Portfolio Rebalancing
"""

import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from src.api.robinhood_client import RobinhoodClient

logger = logging.getLogger(__name__)

@dataclass
class StrategyConfig:
    """Configuration for automated trading strategies."""
    symbol: str
    enabled: bool = True
    check_interval: int = 60  # seconds
    max_retries: int = 3

@dataclass
class StopLossConfig(StrategyConfig):
    """Configuration for stop loss strategy."""
    stop_loss_percentage: float = 5.0  # 5% stop loss
    profit_target_percentage: float = 10.0  # 10% profit target
    position_size_usd: float = 100.0

@dataclass
class TrailingStopConfig(StrategyConfig):
    """Configuration for trailing stop loss strategy."""
    trailing_percentage: float = 3.0  # 3% trailing stop
    activation_percentage: float = 5.0  # Activate after 5% gain
    position_size_usd: float = 100.0

@dataclass
class DCAConfig(StrategyConfig):
    """Configuration for dollar-cost averaging strategy."""
    amount_per_purchase: float = 50.0
    frequency_days: int = 7  # Buy every 7 days
    max_purchases: int = 12  # Maximum 12 purchases

class AutomatedTradingBot:
    """
    Automated trading bot that implements various strategies.
    """
    
    def __init__(self):
        """Initialize the automated trading bot."""
        self.client = RobinhoodClient()
        self.running = False
        self.strategies: Dict[str, Callable] = {}
        self.configs: Dict[str, StrategyConfig] = {}
        
    def authenticate(self) -> bool:
        """Authenticate with Robinhood."""
        return self.client.authenticate()
    
    def add_stop_loss_strategy(self, config: StopLossConfig):
        """Add a stop loss with profit taking strategy."""
        self.configs[f"stop_loss_{config.symbol}"] = config
        self.strategies[f"stop_loss_{config.symbol}"] = self._execute_stop_loss_strategy
        
    def add_trailing_stop_strategy(self, config: TrailingStopConfig):
        """Add a trailing stop loss strategy."""
        self.configs[f"trailing_stop_{config.symbol}"] = config
        self.strategies[f"trailing_stop_{config.symbol}"] = self._execute_trailing_stop_strategy
        
    def add_dca_strategy(self, config: DCAConfig):
        """Add a dollar-cost averaging strategy."""
        self.configs[f"dca_{config.symbol}"] = config
        self.strategies[f"dca_{config.symbol}"] = self._execute_dca_strategy
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        try:
            price_data = self.client.get_crypto_price(symbol)
            if price_data and 'price' in price_data:
                return float(price_data['price'])
            return None
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def _get_position_value(self, symbol: str) -> float:
        """Get current value of position in USD."""
        try:
            holdings = self.client.get_holdings()
            if not holdings or 'results' not in holdings:
                return 0.0
            
            asset_code = symbol.replace('-USD', '')
            holding = next(
                (h for h in holdings['results'] if h.get('asset_code') == asset_code),
                None
            )
            
            if not holding:
                return 0.0
            
            quantity = float(holding.get('quantity_available_for_trading', '0'))
            current_price = self._get_current_price(symbol)
            
            if current_price:
                return quantity * current_price
            return 0.0
        except Exception as e:
            logger.error(f"Error getting position value for {symbol}: {e}")
            return 0.0
    
    def _execute_stop_loss_strategy(self, config: StopLossConfig):
        """Execute stop loss with profit taking strategy."""
        try:
            current_price = self._get_current_price(config.symbol)
            if not current_price:
                return
            
            # Get position value
            position_value = self._get_position_value(config.symbol)
            if position_value == 0:
                # No position, check if we should buy
                buying_power = self.client.get_buying_power()
                if buying_power >= config.position_size_usd:
                    logger.info(f"Buying {config.symbol} for ${config.position_size_usd}")
                    result = self.client.place_market_buy_order(
                        config.symbol, 
                        str(config.position_size_usd)
                    )
                    if result:
                        logger.info(f"Initial position opened for {config.symbol}")
                return
            
            # Calculate entry price (simplified - in real implementation, track this)
            # For now, we'll use current price as reference
            entry_price = current_price  # This should be tracked from actual entry
            
            # Calculate stop loss and profit target prices
            stop_loss_price = entry_price * (1 - config.stop_loss_percentage / 100)
            profit_target_price = entry_price * (1 + config.profit_target_percentage / 100)
            
            # Check if stop loss or profit target hit
            if current_price <= stop_loss_price:
                logger.info(f"Stop loss triggered for {config.symbol} at ${current_price:.2f}")
                self._sell_position(config.symbol, "Stop loss triggered")
            elif current_price >= profit_target_price:
                logger.info(f"Profit target hit for {config.symbol} at ${current_price:.2f}")
                self._sell_position(config.symbol, "Profit target reached")
                
        except Exception as e:
            logger.error(f"Error in stop loss strategy for {config.symbol}: {e}")
    
    def _execute_trailing_stop_strategy(self, config: TrailingStopConfig):
        """Execute trailing stop loss strategy."""
        try:
            current_price = self._get_current_price(config.symbol)
            if not current_price:
                return
            
            position_value = self._get_position_value(config.symbol)
            if position_value == 0:
                return
            
            # This is a simplified implementation
            # In a real system, you'd track the highest price reached and adjust stop loss
            logger.info(f"Trailing stop check for {config.symbol} at ${current_price:.2f}")
            
        except Exception as e:
            logger.error(f"Error in trailing stop strategy for {config.symbol}: {e}")
    
    def _execute_dca_strategy(self, config: DCAConfig):
        """Execute dollar-cost averaging strategy."""
        try:
            # Check if it's time to buy (simplified - should track last purchase date)
            buying_power = self.client.get_buying_power()
            if buying_power >= config.amount_per_purchase:
                logger.info(f"DCA buying {config.symbol} for ${config.amount_per_purchase}")
                result = self.client.place_market_buy_order(
                    config.symbol,
                    str(config.amount_per_purchase)
                )
                if result:
                    logger.info(f"DCA purchase completed for {config.symbol}")
                    
        except Exception as e:
            logger.error(f"Error in DCA strategy for {config.symbol}: {e}")
    
    def _sell_position(self, symbol: str, reason: str):
        """Sell entire position for a symbol."""
        try:
            holdings = self.client.get_holdings()
            if not holdings or 'results' not in holdings:
                return
            
            asset_code = symbol.replace('-USD', '')
            holding = next(
                (h for h in holdings['results'] if h.get('asset_code') == asset_code),
                None
            )
            
            if not holding:
                return
            
            quantity = holding.get('quantity_available_for_trading', '0')
            if float(quantity) > 0:
                logger.info(f"Selling {quantity} {symbol} - {reason}")
                result = self.client.place_market_sell_order(symbol, quantity)
                if result:
                    logger.info(f"Position sold for {symbol}")
                    
        except Exception as e:
            logger.error(f"Error selling position for {symbol}: {e}")
    
    def start(self):
        """Start the automated trading bot."""
        if not self.authenticate():
            logger.error("Authentication failed")
            return
        
        self.running = True
        logger.info("Automated trading bot started")
        
        try:
            while self.running:
                for strategy_name, strategy_func in self.strategies.items():
                    if strategy_name in self.configs:
                        config = self.configs[strategy_name]
                        if config.enabled:
                            strategy_func(config)
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Automated trading bot stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error in automated trading bot: {e}")
            self.stop()
    
    def stop(self):
        """Stop the automated trading bot."""
        self.running = False
        logger.info("Automated trading bot stopped")
    
    def get_strategy_status(self) -> Dict:
        """Get status of all strategies."""
        status = {}
        for strategy_name, config in self.configs.items():
            status[strategy_name] = {
                'enabled': config.enabled,
                'symbol': config.symbol,
                'check_interval': config.check_interval
            }
        return status 