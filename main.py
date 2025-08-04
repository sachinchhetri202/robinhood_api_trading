#!/usr/bin/env python3
"""
Robinhood Crypto Trading CLI

A secure, modern CLI for Robinhood crypto trading.
Author: Sachin Chhetri

This tool allows you to view your crypto portfolio, check prices, and place buy/sell orders on Robinhood from the command line.
"""

import logging
import sys
from typing import List
import click
from dotenv import load_dotenv
from tabulate import tabulate

# Set up logging (default: INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@click.group()
@click.option('--debug', is_flag=True, help="Show detailed debug output.")
def cli(debug):
    """
    Robinhood Crypto Trading CLI

    Securely trade crypto, check your portfolio, and get real-time prices from Robinhood.
    Requires API credentials in a .env file.
    """
    load_dotenv()
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

def validate_auth(bot):
    """
    Ensure the user is authenticated before running any command.
    Exits with an error if authentication fails.
    """
    if not bot.authenticate():
        click.echo("Error: Authentication failed. Please check your credentials.", err=True)
        sys.exit(1)

@cli.command()
def portfolio():
    """
    Display your crypto portfolio and buying power.
    """
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        click.echo(bot.format_portfolio())
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('symbols', nargs=-1, required=True)
def prices(symbols: List[str]):
    """
    Display current prices for one or more crypto symbols (e.g. BTC ETH DOGE).
    """
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        click.echo(bot.format_prices(list(symbols)))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('symbol')
@click.argument('amount', type=click.FloatRange(min=0.01))
def buy(symbol: str, amount: float):
    """
    Place a market buy order for SYMBOL by USD amount.
    Example: python main.py buy BTC 100
    """
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.buy_crypto(symbol, amount)
        if result:
            click.echo(f"✅ Buy order placed: {symbol} for ${amount:.2f}")
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(2)
    except ValueError as e:
        error_msg = str(e)
        if "Insufficient buying power" in error_msg:
            click.echo(f"❌ {error_msg}", err=True)
            click.echo("\n💡 Try a smaller amount or check your buying power with:")
            click.echo("   python main.py buying-power")
        else:
            click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('symbol')
@click.argument('amount', type=click.FloatRange(min=0.01))
def sell(symbol: str, amount: float):
    """
    Place a market sell order for SYMBOL by USD amount.
    Example: python main.py sell DOGE 10
    """
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.sell_crypto(symbol, amount)
        if result:
            click.echo(f"✅ Sell order placed for {symbol}")
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(2)
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
def portfolio_performance():
    """
    Show the best and worst performers in your portfolio by current value.
    Uses only Robinhood data (no external APIs).
    """
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        click.echo(bot.portfolio_performance())
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('symbols', nargs=-1)
def trading_pairs(symbols):
    """
    Display available trading pairs. If no symbols provided, shows all pairs.
    Example: python main.py trading-pairs BTC-USD ETH-USD
    """
    from src.api.robinhood_client import RobinhoodClient
    client = RobinhoodClient()
    validate_auth(client)
    try:
        symbols_list = list(symbols) if symbols else None
        result = client.get_trading_pairs(symbols=symbols_list)
        if result and 'results' in result:
            rows = []
            for pair in result['results']:
                symbol = pair.get('symbol', 'N/A')
                status = pair.get('status', 'N/A')
                rows.append([symbol, status])
            table = tabulate(rows, headers=['Symbol', 'Status'], tablefmt='grid')
            click.echo(table)
        else:
            click.echo("No trading pairs found or error occurred.")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.option('--symbol', help='Filter by symbol (e.g., BTC-USD)')
@click.option('--side', type=click.Choice(['buy', 'sell']), help='Filter by side')
@click.option('--state', type=click.Choice(['open', 'canceled', 'partially_filled', 'filled', 'failed']), help='Filter by state')
@click.option('--type', 'order_type', type=click.Choice(['limit', 'market', 'stop_limit', 'stop_loss']), help='Filter by order type')
@click.option('--limit', type=int, help='Limit number of results')
def orders(symbol, side, state, order_type, limit):
    """
    Display your crypto orders with optional filtering.
    Example: python main.py orders --symbol BTC-USD --state open
    """
    from src.api.robinhood_client import RobinhoodClient
    from tabulate import tabulate
    client = RobinhoodClient()
    validate_auth(client)
    try:
        result = client.get_orders(
            symbol=symbol,
            side=side,
            state=state,
            order_type=order_type,
            limit=limit
        )
        if result and 'results' in result:
            rows = []
            for order in result['results']:
                rows.append([
                    order.get('id', 'N/A'),
                    order.get('symbol', 'N/A'),
                    order.get('side', 'N/A'),
                    order.get('type', 'N/A'),
                    order.get('state', 'N/A'),
                    order.get('created_at', 'N/A')[:19] if order.get('created_at') else 'N/A'
                ])
            table = tabulate(rows, headers=['ID', 'Symbol', 'Side', 'Type', 'State', 'Created'], tablefmt='grid')
            click.echo(table)
        else:
            click.echo("No orders found or error occurred.")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('order_id')
def cancel(order_id):
    """
    Cancel an open order by its ID.
    Example: python main.py cancel 12345678-1234-1234-1234-123456789012
    """
    from src.api.robinhood_client import RobinhoodClient
    client = RobinhoodClient()
    validate_auth(client)
    try:
        success = client.cancel_order(order_id)
        if success:
            click.echo(f"✅ Order {order_id} cancellation request submitted")
        else:
            click.echo("❌ Failed to cancel order", err=True)
            sys.exit(2)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
def buying_power():
    """
    Display your current buying power.
    """
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        buying_power = bot.get_buying_power()
        click.echo(f"💰 Current Buying Power: ${buying_power:,.2f}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('symbol')
@click.option('--stop-loss', default=5.0, help='Stop loss percentage (default: 5.0)')
@click.option('--profit-target', default=10.0, help='Profit target percentage (default: 10.0)')
@click.option('--position-size', default=100.0, help='Position size in USD (default: 100.0)')
def stop_loss_strategy(symbol: str, stop_loss: float, profit_target: float, position_size: float):
    """
    Set up a stop loss with profit taking strategy for a symbol.
    Example: python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 15.0
    """
    from src.trading.automated_strategies import AutomatedTradingBot, StopLossConfig
    bot = AutomatedTradingBot()
    validate_auth(bot)
    
    try:
        if not symbol.endswith('-USD'):
            symbol = f"{symbol}-USD"
        
        config = StopLossConfig(
            symbol=symbol,
            stop_loss_percentage=stop_loss,
            profit_target_percentage=profit_target,
            position_size_usd=position_size
        )
        
        bot.add_stop_loss_strategy(config)
        click.echo(f"✅ Stop loss strategy configured for {symbol}")
        click.echo(f"   Stop Loss: {stop_loss}%")
        click.echo(f"   Profit Target: {profit_target}%")
        click.echo(f"   Position Size: ${position_size}")
        click.echo("\n💡 To start automated trading, use: python main.py auto-trade")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
@click.argument('symbol')
@click.option('--amount', default=50.0, help='Amount per purchase in USD (default: 50.0)')
@click.option('--frequency', default=7, help='Purchase frequency in days (default: 7)')
@click.option('--max-purchases', default=12, help='Maximum number of purchases (default: 12)')
def dca_strategy(symbol: str, amount: float, frequency: int, max_purchases: int):
    """
    Set up a dollar-cost averaging (DCA) strategy for a symbol.
    Example: python main.py dca-strategy BTC --amount 25 --frequency 14
    """
    from src.trading.automated_strategies import AutomatedTradingBot, DCAConfig
    bot = AutomatedTradingBot()
    validate_auth(bot)
    
    try:
        if not symbol.endswith('-USD'):
            symbol = f"{symbol}-USD"
        
        config = DCAConfig(
            symbol=symbol,
            amount_per_purchase=amount,
            frequency_days=frequency,
            max_purchases=max_purchases
        )
        
        bot.add_dca_strategy(config)
        click.echo(f"✅ DCA strategy configured for {symbol}")
        click.echo(f"   Amount per purchase: ${amount}")
        click.echo(f"   Frequency: Every {frequency} days")
        click.echo(f"   Max purchases: {max_purchases}")
        click.echo("\n💡 To start automated trading, use: python main.py auto-trade")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

@cli.command()
def auto_trade():
    """
    Start automated trading with configured strategies.
    Press Ctrl+C to stop.
    """
    from src.trading.automated_strategies import AutomatedTradingBot
    bot = AutomatedTradingBot()
    validate_auth(bot)
    
    try:
        click.echo("🤖 Starting automated trading bot...")
        click.echo("Press Ctrl+C to stop")
        bot.start()
    except KeyboardInterrupt:
        click.echo("\n🛑 Automated trading stopped")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(2)

if __name__ == '__main__':
    cli() 