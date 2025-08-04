#!/usr/bin/env python3
"""
Automated Trading Example

This script demonstrates how to set up and use automated trading strategies.
Run this script to see automated trading in action.

Author: Sachin Chhetri
"""

import time
import logging
from src.trading.automated_strategies import AutomatedTradingBot, StopLossConfig, DCAConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    """Main function to demonstrate automated trading."""
    print("🤖 Automated Trading Strategy Example")
    print("=" * 50)
    
    # Initialize the automated trading bot
    bot = AutomatedTradingBot()
    
    # Authenticate with Robinhood
    print("🔐 Authenticating with Robinhood...")
    if not bot.authenticate():
        print("❌ Authentication failed. Please check your credentials.")
        return
    
    print("✅ Authentication successful!")
    
    # Set up a stop loss strategy for Bitcoin
    print("\n📊 Setting up Stop Loss Strategy for BTC...")
    stop_loss_config = StopLossConfig(
        symbol="BTC-USD",
        stop_loss_percentage=5.0,  # 5% stop loss
        profit_target_percentage=10.0,  # 10% profit target
        position_size_usd=50.0  # Start with $50
    )
    bot.add_stop_loss_strategy(stop_loss_config)
    print("✅ Stop loss strategy configured")
    
    # Set up a DCA strategy for Ethereum
    print("\n📈 Setting up DCA Strategy for ETH...")
    dca_config = DCAConfig(
        symbol="ETH-USD",
        amount_per_purchase=25.0,  # Buy $25 at a time
        frequency_days=7,  # Every 7 days
        max_purchases=6  # Maximum 6 purchases
    )
    bot.add_dca_strategy(dca_config)
    print("✅ DCA strategy configured")
    
    # Show strategy status
    print("\n📋 Strategy Status:")
    status = bot.get_strategy_status()
    for strategy_name, config in status.items():
        print(f"   {strategy_name}: {config['symbol']} - {'✅ Enabled' if config['enabled'] else '❌ Disabled'}")
    
    print("\n🚀 Starting automated trading...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start the automated trading bot
        bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping automated trading...")
        bot.stop()
        print("✅ Automated trading stopped safely")

if __name__ == "__main__":
    main() 