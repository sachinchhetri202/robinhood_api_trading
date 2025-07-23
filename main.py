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
        click.echo(f"Error: {str(e)}", err=True)
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

if __name__ == '__main__':
    cli() 