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

from src.config.settings import settings
from src.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)

# Exit codes:
# 0 = success
# 1 = user/input/auth/configuration errors
# 2 = API/network/unexpected errors
EXIT_CODE_USER_ERROR = 1
EXIT_CODE_SYSTEM_ERROR = 2

@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, help="Show detailed debug output.")
@click.option('--log-file', is_flag=True, help="Write logs to ~/.robinhood_trading/logs/")
@click.pass_context
def cli(ctx, debug, log_file):
    """
    Robinhood Crypto Trading CLI

    Securely trade crypto, check your portfolio, and get real-time prices from Robinhood.
    Run without a subcommand to start an interactive trading shell.
    Requires API credentials in a .env file.
    """
    try:
        load_dotenv()
    except PermissionError:
        pass
    settings.reload()
    configure_logging(debug=debug, log_to_file=log_file or settings.LOG_TO_FILE, log_dir=settings.LOG_DIR)
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

    if ctx.invoked_subcommand is None:
        start_interactive_shell()


def start_interactive_shell():
    """Start an interactive shell for trading commands."""
    import shlex
    import sys

    if not sys.stdin.isatty():
        click.echo("Interactive shell requires a terminal (TTY).", err=True)
        click.echo("Run: python main.py  (from a real terminal window)", err=True)
        return

    click.echo("Robinhood Trading Shell")
    click.echo("Type commands like 'portfolio', 'prices BTC', 'portfolio-stats'.")
    click.echo("Type 'help' for full command list, 'exit' to quit.")
    while True:
        try:
            user_input = input("trading> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nExiting shell.")
            break
        if not user_input:
            continue
        if user_input in {"exit", "quit"}:
            break
        if user_input in {"help", "--help", "-h"}:
            try:
                cli.main(args=["--help"], prog_name="main.py", standalone_mode=False)
            except SystemExit:
                pass
            continue
        try:
            args = shlex.split(user_input)
            cli.main(args=args, prog_name="main.py", standalone_mode=False)
        except click.ClickException as e:
            # Show Click's formatted error and keep the shell running
            e.show()
            continue
        except SystemExit:
            # Prevent shell from exiting on command errors
            continue

def validate_auth(bot):
    """
    Ensure the user is authenticated before running any command.
    Exits with an error if authentication fails.
    """
    # Check if credentials are set before attempting authentication
    if not settings.API_KEY or not settings.BASE64_PRIVATE_KEY:
        click.echo("Error: Missing API credentials.", err=True)
        click.echo("\nPlease add the following to your .env file:", err=True)
        click.echo("  API_KEY=your_api_key_here", err=True)
        click.echo("  BASE64_PRIVATE_KEY=your_base64_encoded_private_key_here", err=True)
        click.echo("\nRun 'python generate_keypair.py' to generate a keypair if needed.", err=True)
        sys.exit(EXIT_CODE_USER_ERROR)
    
    try:
        if not bot.authenticate():
            click.echo("Error: Authentication failed. Please check your credentials.", err=True)
            click.echo("\nCommon issues:", err=True)
            click.echo("  - API_KEY or BASE64_PRIVATE_KEY may be incorrect", err=True)
            click.echo("  - Your API key may not have the required permissions", err=True)
            click.echo("  - Your account may not have crypto trading enabled", err=True)
            sys.exit(EXIT_CODE_USER_ERROR)
    except ValueError as e:
        # Handle credential validation errors from RobinhoodClient
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_USER_ERROR)

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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except ValueError as e:
        error_msg = str(e)
        if "Insufficient buying power" in error_msg:
            click.echo(f"❌ {error_msg}", err=True)
            click.echo("\n💡 Try a smaller amount or check your buying power with:")
            click.echo("   python main.py buying-power")
        else:
            click.echo(f"Error: {error_msg}", err=True)
        sys.exit(EXIT_CODE_USER_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_USER_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
    from src.utils.symbols import normalize_symbol_to_usd
    bot = AutomatedTradingBot()
    validate_auth(bot)
    
    try:
        symbol = normalize_symbol_to_usd(symbol)
        
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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
    from src.utils.symbols import normalize_symbol_to_usd
    bot = AutomatedTradingBot()
    validate_auth(bot)
    
    try:
        symbol = normalize_symbol_to_usd(symbol)
        
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
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

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
        bot.load_strategies()
        bot.start()
    except KeyboardInterrupt:
        click.echo("\n🛑 Automated trading stopped")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
def list_strategies():
    """List configured automated strategies."""
    from src.trading.automated_strategies import AutomatedTradingBot
    bot = AutomatedTradingBot()
    validate_auth(bot)
    bot.load_strategies()
    strategies = bot.list_strategies()
    if not strategies:
        click.echo("No strategies configured.")
        return
    rows = []
    for key, config in strategies.items():
        rows.append([key, config.symbol, "✅ Enabled" if config.enabled else "❌ Disabled"])
    table = tabulate(rows, headers=["Key", "Symbol", "Status"], tablefmt="grid")
    click.echo(table)

@cli.command()
@click.argument("strategy_key")
def remove_strategy(strategy_key):
    """Remove a configured strategy by key."""
    from src.trading.automated_strategies import AutomatedTradingBot
    bot = AutomatedTradingBot()
    validate_auth(bot)
    bot.load_strategies()
    if bot.remove_strategy(strategy_key):
        click.echo(f"✅ Removed strategy {strategy_key}")
    else:
        click.echo("Strategy not found.", err=True)
        sys.exit(EXIT_CODE_USER_ERROR)

@cli.command()
def load_strategies():
    """Load strategies from disk into the bot."""
    from src.trading.automated_strategies import AutomatedTradingBot
    bot = AutomatedTradingBot()
    validate_auth(bot)
    bot.load_strategies()
    click.echo("✅ Strategies loaded from disk")

@cli.command()
def portfolio_stats():
    """Show detailed portfolio statistics."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        click.echo(bot.portfolio_stats())
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.option("--symbol", help="Filter by symbol (e.g., BTC-USD)")
@click.option("--limit", type=int, help="Limit number of results")
def trade_history(symbol, limit):
    """Show trade history (filled orders)."""
    from src.trading.trading_bot import TradingBot
    from src.analytics.trade_history import format_trade_history
    bot = TradingBot()
    validate_auth(bot)
    try:
        orders = bot.trade_history(symbol=symbol, limit=limit)
        click.echo(format_trade_history(orders))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.argument("symbol")
@click.argument("amount", type=click.FloatRange(min=0.00000001))
@click.argument("limit_price", type=click.FloatRange(min=0.01))
def limit_buy(symbol: str, amount: float, limit_price: float):
    """Place a limit buy order for SYMBOL by asset quantity and price."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.place_limit_order(symbol, "buy", amount, limit_price)
        if result:
            click.echo(f"✅ Limit buy order placed: {symbol} {amount} @ ${limit_price}")
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.argument("symbol")
@click.argument("amount", type=click.FloatRange(min=0.00000001))
@click.argument("limit_price", type=click.FloatRange(min=0.01))
def limit_sell(symbol: str, amount: float, limit_price: float):
    """Place a limit sell order for SYMBOL by asset quantity and price."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.place_limit_order(symbol, "sell", amount, limit_price)
        if result:
            click.echo(f"✅ Limit sell order placed: {symbol} {amount} @ ${limit_price}")
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.argument("symbol")
@click.argument("amount", type=click.FloatRange(min=0.00000001))
@click.argument("stop_price", type=click.FloatRange(min=0.01))
def stop_loss_buy(symbol: str, amount: float, stop_price: float):
    """Place a stop loss buy order for SYMBOL by asset quantity and stop price."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.place_stop_loss_order(symbol, "buy", amount, stop_price)
        if result:
            click.echo(f"✅ Stop loss buy order placed: {symbol} {amount} @ ${stop_price}")
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.argument("symbol")
@click.argument("amount", type=click.FloatRange(min=0.00000001))
@click.argument("stop_price", type=click.FloatRange(min=0.01))
def stop_loss_sell(symbol: str, amount: float, stop_price: float):
    """Place a stop loss sell order for SYMBOL by asset quantity and stop price."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.place_stop_loss_order(symbol, "sell", amount, stop_price)
        if result:
            click.echo(f"✅ Stop loss sell order placed: {symbol} {amount} @ ${stop_price}")
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.argument("symbol")
@click.argument("amount", type=click.FloatRange(min=0.00000001))
@click.argument("limit_price", type=click.FloatRange(min=0.01))
@click.argument("stop_price", type=click.FloatRange(min=0.01))
def stop_limit_buy(symbol: str, amount: float, limit_price: float, stop_price: float):
    """Place a stop limit buy order for SYMBOL by asset quantity and prices."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.place_stop_limit_order(symbol, "buy", amount, limit_price, stop_price)
        if result:
            click.echo(
                f"✅ Stop limit buy order placed: {symbol} {amount} @ ${limit_price} (stop ${stop_price})"
            )
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

@cli.command()
@click.argument("symbol")
@click.argument("amount", type=click.FloatRange(min=0.00000001))
@click.argument("limit_price", type=click.FloatRange(min=0.01))
@click.argument("stop_price", type=click.FloatRange(min=0.01))
def stop_limit_sell(symbol: str, amount: float, limit_price: float, stop_price: float):
    """Place a stop limit sell order for SYMBOL by asset quantity and prices."""
    from src.trading.trading_bot import TradingBot
    bot = TradingBot()
    validate_auth(bot)
    try:
        result = bot.place_stop_limit_order(symbol, "sell", amount, limit_price, stop_price)
        if result:
            click.echo(
                f"✅ Stop limit sell order placed: {symbol} {amount} @ ${limit_price} (stop ${stop_price})"
            )
            click.echo(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            click.echo("❌ Order failed", err=True)
            sys.exit(EXIT_CODE_SYSTEM_ERROR)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(EXIT_CODE_SYSTEM_ERROR)

if __name__ == '__main__':
    cli() 