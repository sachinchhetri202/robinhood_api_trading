"""
TradingBot: Thin business logic layer for Robinhood CLI

Author: Sachin Chhetri

This class provides user-friendly methods for portfolio display, price lookup, and trading operations.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from tabulate import tabulate
from src.api.robinhood_client import RobinhoodClient
from src.analytics.portfolio_analyzer import compute_portfolio_stats
from src.utils.symbols import normalize_symbol_to_usd, validate_symbol

logger = logging.getLogger(__name__)

class TradingBot:
    """
    Thin wrapper around RobinhoodClient for CLI use.
    Handles formatting, symbol normalization, and user-friendly error messages.
    """
    def __init__(self):
        """
        Initialize the trading bot with a RobinhoodClient instance.
        """
        self.client = RobinhoodClient()

    def authenticate(self) -> bool:
        """
        Authenticate with Robinhood. Returns True if successful.
        """
        return self.client.authenticate()

    def get_buying_power(self) -> float:
        """
        Get current buying power from the account.
        """
        return self.client.get_buying_power()

    def check_buying_power_for_order(self, amount: float) -> bool:
        """
        Check if there's enough buying power for a given USD amount.
        Returns True if sufficient, False otherwise.
        """
        buying_power = self.get_buying_power()
        return buying_power >= amount

    def format_portfolio(self) -> str:
        """
        Fetch and format the user's crypto portfolio as a table.
        """
        holdings = self.client.get_holdings()
        if not holdings or 'results' not in holdings:
            return "No holdings found."
        rows = []
        total_value = Decimal('0')
        for holding in holdings['results']:
            asset_code = holding.get('asset_code') or holding.get('symbol', 'UNKNOWN').replace('-USD', '')
            symbol = f"{asset_code}-USD"
            quantity = Decimal(
                holding.get('quantity_available_for_trading')
                or holding.get('quantity')
                or '0'
            )
            # Get current price for this asset
            price_data = self.client.get_crypto_price(symbol)
            current_price = Decimal(price_data.get('price', '0')) if price_data else Decimal('0')
            market_value = quantity * current_price
            total_value += market_value
            rows.append([
                symbol,
                f"{quantity:.8f}",
                f"${current_price:.2f}",
                f"${market_value:.2f}"
            ])
        rows.append(['TOTAL', '', '', f"${total_value:.2f}"])
        table = tabulate(
            rows,
            headers=['Symbol', 'Quantity', 'Price', 'Value'],
            tablefmt='grid'
        )
        buying_power = self.client.get_buying_power()
        return f"{table}\n\nBuying Power: ${buying_power:,.2f}"

    def format_prices(self, symbols: List[str]) -> str:
        """
        Fetch and format current prices for a list of symbols.
        """
        if not symbols:
            return "No symbols provided."
        rows = []
        for symbol in symbols:
            symbol = normalize_symbol_to_usd(symbol)
            price_data = self.client.get_crypto_price(symbol)
            if price_data:
                price = Decimal(price_data.get('price', '0'))
                if price < Decimal("1"):
                    price_display = f"${price:.8f}".rstrip("0").rstrip(".")
                else:
                    price_display = f"${price:.2f}"
                rows.append([symbol, price_display])
            else:
                rows.append([symbol, 'N/A'])
        return tabulate(
            rows,
            headers=['Symbol', 'Price'],
            tablefmt='grid'
        )

    def buy_crypto(self, symbol: str, amount: float) -> Optional[Dict]:
        """
        Place a market buy order for a symbol and USD amount.
        """
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not validate_symbol(symbol):
            raise ValueError("Invalid symbol format")
        symbol = normalize_symbol_to_usd(symbol)
        
        # Check buying power before attempting to place order
        buying_power = self.client.get_buying_power()
        if buying_power < amount:
            raise ValueError(
                f"Insufficient buying power\n"
                f"Requested: ${amount:.2f}\n"
                f"Available: ${buying_power:.2f}\n"
                f"Shortfall: ${amount - buying_power:.2f}"
            )
        
        result = self.client.place_market_buy_order(
            symbol=symbol,
            quote_amount=str(amount)
        )
        if result:
            logger.info(f"Buy order placed: {symbol} for ${amount:.2f}")
            logger.info(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            logger.error(f"Failed to place buy order for {symbol}")
        return result

    def sell_crypto(self, symbol: str, amount: float) -> Optional[Dict]:
        """
        Place a market sell order for a symbol and USD amount.
        """
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not validate_symbol(symbol):
            raise ValueError("Invalid symbol format")
        symbol = normalize_symbol_to_usd(symbol)
        holdings = self.client.get_holdings()
        if not holdings or 'results' not in holdings:
            raise ValueError("No holdings found")
        asset_code = symbol.replace('-USD', '')
        holding = next(
            (
                h for h in holdings['results']
                if h.get('asset_code') == asset_code
                or h.get('symbol') == symbol
                or h.get('symbol') == asset_code
            ),
            None
        )
        if not holding:
            raise ValueError(f"No {symbol} holdings found")
        price_data = self.client.get_crypto_price(symbol)
        if not price_data:
            raise RuntimeError(f"Could not get current price for {symbol}")
        current_price = Decimal(price_data.get('price', '0'))
        if current_price == 0:
            raise RuntimeError(f"Invalid price data for {symbol}")
        quantity_to_sell = Decimal(str(amount)) / current_price
        # Round to 8 decimal places to avoid Robinhood's decimal place limit
        quantity_to_sell_rounded = quantity_to_sell.quantize(Decimal('0.00000001'), rounding='ROUND_DOWN')
        
        current_quantity = Decimal(
            holding.get('quantity_available_for_trading')
            or holding.get('quantity')
            or '0'
        )
        if quantity_to_sell_rounded > current_quantity:
            raise ValueError(
                f"Insufficient {symbol} balance\n"
                f"Requested: {quantity_to_sell_rounded:.8f}\n"
                f"Available: {current_quantity:.8f}"
            )
        result = self.client.place_market_sell_order(
            symbol=symbol,
            asset_quantity=str(quantity_to_sell_rounded)
        )
        if result:
            logger.info(f"Sell order placed: {quantity_to_sell_rounded:.8f} {symbol}")
            logger.info(f"Order ID: {result.get('id', 'Unknown')}")
        else:
            logger.error(f"Failed to place sell order for {symbol}")
        return result

    def portfolio_performance(self) -> str:
        """
        Show the best and worst performers in your portfolio by current value.
        Uses only Robinhood data (no external APIs).
        """
        holdings = self.client.get_holdings()
        if not holdings or 'results' not in holdings:
            return "No holdings found."
        performance = []
        for holding in holdings['results']:
            asset_code = holding.get('asset_code') or holding.get('symbol', 'UNKNOWN').replace('-USD', '')
            symbol = f"{asset_code}-USD"
            quantity = Decimal(
                holding.get('quantity_available_for_trading')
                or holding.get('quantity')
                or '0'
            )
            price_data = self.client.get_crypto_price(symbol)
            current_price = Decimal(price_data.get('price', '0')) if price_data else Decimal('0')
            value = quantity * current_price
            performance.append({
                'symbol': symbol,
                'quantity': quantity,
                'price': current_price,
                'value': value
            })
        # Sort by value descending
        performance_sorted = sorted(performance, key=lambda x: x['value'], reverse=True)
        top = performance_sorted[:3]
        bottom = performance_sorted[-3:][::-1]  # Show lowest 3
        def perf_table(perf_list, title):
            rows = [
                [p['symbol'], f"{p['quantity']:.8f}", f"${p['price']:.2f}", f"${p['value']:.2f}"]
                for p in perf_list
            ]
            return f"\n{title}\n" + tabulate(
                rows,
                headers=['Symbol', 'Quantity', 'Price', 'Value'],
                tablefmt='grid'
            )
        result = perf_table(top, "Top 3 Performers (by value)")
        result += perf_table(bottom, "\nWorst 3 Performers (by value)")
        return result

    def portfolio_stats(self) -> str:
        """Return detailed portfolio stats."""
        holdings = self.client.get_holdings()
        if not holdings or "results" not in holdings:
            return "No holdings found."
        prices = {}
        for holding in holdings["results"]:
            asset_code = holding.get("asset_code") or holding.get("symbol", "UNKNOWN").replace("-USD", "")
            symbol = f"{asset_code}-USD"
            price_data = self.client.get_crypto_price(symbol)
            prices[symbol] = price_data.get("price", "0") if price_data else "0"
        buying_power = self.client.get_buying_power()
        stats = compute_portfolio_stats(holdings, prices, buying_power)
        rows = [
            [
                p["symbol"],
                f"{p['quantity']:.8f}",
                f"${p['price']:.2f}",
                f"${p['value']:.2f}",
            ]
            for p in stats["positions"]
        ]
        table = tabulate(
            rows,
            headers=["Symbol", "Quantity", "Price", "Value"],
            tablefmt="grid",
        )
        total_value = stats["total_value"]
        return f"{table}\n\nTotal Value: ${total_value:.2f}\nBuying Power: ${buying_power:,.2f}"

    def trade_history(self, symbol: Optional[str] = None, limit: Optional[int] = None) -> Dict:
        """Fetch filled orders as trade history."""
        return self.client.get_orders(symbol=symbol, state="filled", limit=limit) or {"results": []}

    def place_limit_order(self, symbol: str, side: str, amount: float, limit_price: float) -> Optional[Dict]:
        """Place a limit order."""
        if amount <= 0 or limit_price <= 0:
            raise ValueError("Amount and limit price must be greater than 0")
        if not validate_symbol(symbol):
            raise ValueError("Invalid symbol format")
        symbol = normalize_symbol_to_usd(symbol)
        return self.client.place_limit_order(symbol, side, str(amount), str(limit_price))

    def place_stop_loss_order(self, symbol: str, side: str, amount: float, stop_price: float) -> Optional[Dict]:
        """Place a stop loss order."""
        if amount <= 0 or stop_price <= 0:
            raise ValueError("Amount and stop price must be greater than 0")
        if not validate_symbol(symbol):
            raise ValueError("Invalid symbol format")
        symbol = normalize_symbol_to_usd(symbol)
        return self.client.place_stop_loss_order(symbol, side, str(amount), str(stop_price))

    def place_stop_limit_order(
        self, symbol: str, side: str, amount: float, limit_price: float, stop_price: float
    ) -> Optional[Dict]:
        """Place a stop limit order."""
        if amount <= 0 or limit_price <= 0 or stop_price <= 0:
            raise ValueError("Amount, limit price, and stop price must be greater than 0")
        if not validate_symbol(symbol):
            raise ValueError("Invalid symbol format")
        symbol = normalize_symbol_to_usd(symbol)
        return self.client.place_stop_limit_order(
            symbol, side, str(amount), str(limit_price), str(stop_price)
        )