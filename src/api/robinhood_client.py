"""
Robinhood API Client

A secure, modern Python API client for Robinhood crypto trading.
Author: Sachin Chhetri

Handles authentication, signing, and all core crypto trading API calls.
"""

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List
import requests
from nacl.signing import SigningKey
from src.config.settings import settings

class RobinhoodClient:
    """
    Main API client for Robinhood crypto trading.
    Handles authentication, signing, and all trading/portfolio operations.
    """
    # API Endpoints
    ACCOUNTS_ENDPOINT = '/api/v1/crypto/trading/accounts/'
    HOLDINGS_ENDPOINT = '/api/v1/crypto/trading/holdings/'
    ORDERS_ENDPOINT = '/api/v1/crypto/trading/orders/'
    PRICES_ENDPOINT = '/api/v1/crypto/marketdata/best_bid_ask/'
    TRADING_PAIRS_ENDPOINT = '/api/v1/crypto/trading/trading_pairs/'

    def __init__(self):
        """
        Initialize the client, set up logging, and prepare signing key.
        """
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.is_authenticated = False
        # Prepare Ed25519 signing key
        private_key_seed = base64.b64decode(settings.BASE64_PRIVATE_KEY)
        self.private_key = SigningKey(private_key_seed)
        # Do not set log level here; let main CLI control it

    @staticmethod
    def _get_current_timestamp() -> int:
        """Get current UTC timestamp in seconds."""
        return int(datetime.now(tz=timezone.utc).timestamp())

    @staticmethod
    def _round_asset_quantity(asset_quantity: str) -> str:
        """
        Round asset quantity to 8 decimal places to comply with Robinhood's requirements.
        This prevents the "must have at most 18 decimal places" error.
        """
        from decimal import Decimal
        try:
            quantity = Decimal(asset_quantity)
            rounded = quantity.quantize(Decimal('0.00000001'), rounding='ROUND_DOWN')
            return str(rounded)
        except (ValueError, TypeError):
            # If conversion fails, return original value
            return asset_quantity

    def _sign_request(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """
        Sign a request using Ed25519 and return the required headers.
        """
        try:
            timestamp = self._get_current_timestamp()
            message = f"{settings.API_KEY}{timestamp}{path}{method}{body}"
            self.logger.debug(f"Signing request - Method: {method}, Path: {path}")
            self.logger.debug(f"Message to sign: {message}")
            signed = self.private_key.sign(message.encode('utf-8'))
            signature_b64 = base64.b64encode(signed.signature).decode('utf-8')
            return {
                'x-api-key': settings.API_KEY,
                'x-timestamp': str(timestamp),
                'x-signature': signature_b64
            }
        except Exception as e:
            self.logger.error(f"Error signing request: {str(e)}")
            raise

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make an authenticated request to the Robinhood API.
        Handles signing, error logging, and returns JSON response.
        """
        try:
            url = f"https://trading.robinhood.com{endpoint}"
            self.logger.debug(f"Making request to: {url}")
            self.logger.debug(f"Method: {method}")
            self.logger.debug(f"Kwargs: {kwargs}")
            body = ""
            if 'json' in kwargs:
                body = json.dumps(kwargs['json'])
                self.logger.debug(f"Request body: {body}")
            headers = self._sign_request(method, endpoint, body)
            if 'json' in kwargs:
                headers['Content-Type'] = 'application/json'
            self.logger.debug(f"Request headers: {headers}")
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=10,
                **kwargs
            )
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Response headers: {dict(response.headers)}")
            if response.status_code in [200, 201]:
                resp_json = response.json()
                self.logger.debug(f"Response JSON: {resp_json}")
                return resp_json
            else:
                self.logger.error(f"API request failed: {response.status_code}")
                try:
                    self.logger.error(f"Response content: {response.text}")
                except:
                    pass
                return None
        except requests.exceptions.Timeout:
            self.logger.error("Request timeout")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            return None

    def authenticate(self) -> bool:
        """
        Authenticate with Robinhood by making a test call to the accounts endpoint.
        Returns True if successful, False otherwise.
        """
        try:
            self.logger.info("Attempting authentication...")
            response = self._make_request('GET', self.ACCOUNTS_ENDPOINT)
            if response:
                self.is_authenticated = True
                self.logger.info("Successfully authenticated with Robinhood")
                return True
            else:
                self.logger.error("Authentication failed")
                return False
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False

    def get_account(self) -> Optional[Dict]:
        """Get crypto trading account details."""
        return self._make_request('GET', self.ACCOUNTS_ENDPOINT)

    def get_holdings(self) -> Optional[Dict]:
        """Get crypto holdings for the account."""
        return self._make_request('GET', self.HOLDINGS_ENDPOINT)

    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """
        Get the current price for a crypto symbol (e.g., BTC-USD).
        """
        try:
            response = self._make_request('GET', f'{self.PRICES_ENDPOINT}?symbol={symbol.upper()}')
            if response and 'results' in response and response['results']:
                return response['results'][0]
            else:
                self.logger.warning(f"No price data for {symbol}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None

    def place_market_buy_order(self, symbol: str, quote_amount: str) -> Optional[Dict]:
        """
        Place a market buy order for a given symbol and USD amount.
        Robinhood API requires asset_quantity for market orders, so we calculate it from the current price.
        """
        try:
            import uuid
            from decimal import Decimal
            
            # Get current price to calculate asset quantity
            price_data = self.get_crypto_price(symbol)
            if not price_data or 'price' not in price_data:
                self.logger.error(f"Could not get current price for {symbol}")
                return None
            
            current_price = Decimal(price_data['price'])
            if current_price <= 0:
                self.logger.error(f"Invalid price for {symbol}: {current_price}")
                return None
            
            # Calculate asset quantity from USD amount
            quote_amount_decimal = Decimal(quote_amount)
            asset_quantity = quote_amount_decimal / current_price
            
            # Round to 8 decimal places (standard for most cryptocurrencies)
            # This ensures we don't exceed Robinhood's 18 decimal place limit
            asset_quantity_rounded = asset_quantity.quantize(Decimal('0.00000001'), rounding='ROUND_DOWN')
            
            order_data = {
                "client_order_id": str(uuid.uuid4()),
                "symbol": symbol.upper(),
                "side": "buy",
                "type": "market",
                "market_order_config": {
                    "asset_quantity": str(asset_quantity_rounded)
                }
            }
            self.logger.info(f"Placing market buy order: {symbol} for ${quote_amount} (≈ {asset_quantity_rounded} {symbol.replace('-USD', '')})")
            return self._make_request('POST', self.ORDERS_ENDPOINT, json=order_data)
        except Exception as e:
            self.logger.error(f"Error placing market buy order: {str(e)}")
            return None

    def place_market_sell_order(self, symbol: str, asset_quantity: str) -> Optional[Dict]:
        """
        Place a market sell order for a given symbol and asset quantity.
        """
        try:
            import uuid
            order_data = {
                "client_order_id": str(uuid.uuid4()),
                "symbol": symbol.upper(),
                "side": "sell",
                "type": "market",
                "market_order_config": {
                    "asset_quantity": self._round_asset_quantity(asset_quantity)
                }
            }
            self.logger.info(f"Placing market sell order: {asset_quantity} {symbol}")
            return self._make_request('POST', self.ORDERS_ENDPOINT, json=order_data)
        except Exception as e:
            self.logger.error(f"Error placing market sell order: {str(e)}")
            return None

    def get_buying_power(self) -> float:
        """
        Get current buying power from the crypto trading account.
        """
        try:
            account = self.get_account()
            if account and 'buying_power' in account:
                buying_power = float(account['buying_power'])
                self.logger.info(f"Retrieved buying power: ${buying_power:,.2f}")
                return buying_power
            self.logger.warning("No buying power found in account")
            return 0.00
        except Exception as e:
            self.logger.error(f"Error getting buying power: {str(e)}")
            return 0.00

    def get_trading_pairs(self, symbols: Optional[List[str]] = None, limit: Optional[int] = None) -> Optional[Dict]:
        """
        Get crypto trading pairs.
        
        Args:
            symbols: List of trading pair symbols (e.g., ['BTC-USD', 'ETH-USD'])
            limit: Limit the number of results per page size
        """
        try:
            params = {}
            if symbols:
                for symbol in symbols:
                    params.setdefault('symbol', []).append(symbol.upper())
            if limit:
                params['limit'] = limit
            
            query_string = '&'.join([f"{k}={v}" if not isinstance(v, list) else '&'.join([f"{k}={item}" for item in v]) for k, v in params.items()])
            endpoint = f"{self.TRADING_PAIRS_ENDPOINT}?{query_string}" if query_string else self.TRADING_PAIRS_ENDPOINT
            
            return self._make_request('GET', endpoint)
        except Exception as e:
            self.logger.error(f"Error getting trading pairs: {str(e)}")
            return None

    def get_orders(self, 
                   symbol: Optional[str] = None,
                   side: Optional[str] = None,
                   state: Optional[str] = None,
                   order_type: Optional[str] = None,
                   limit: Optional[int] = None,
                   created_at_start: Optional[str] = None,
                   created_at_end: Optional[str] = None,
                   updated_at_start: Optional[str] = None,
                   updated_at_end: Optional[str] = None) -> Optional[Dict]:
        """
        Get crypto orders for the current user.
        
        Args:
            symbol: Currency pair symbol (e.g., 'BTC-USD')
            side: 'buy' or 'sell'
            state: 'open', 'canceled', 'partially_filled', 'filled', 'failed'
            order_type: 'limit', 'market', 'stop_limit', 'stop_loss'
            limit: Limit the number of results per page size
            created_at_start: Filter by created at start time (ISO 8601 format)
            created_at_end: Filter by created at end time (ISO 8601 format)
            updated_at_start: Filter by updated at start time (ISO 8601 format)
            updated_at_end: Filter by updated at end time (ISO 8601 format)
        """
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol.upper()
            if side:
                params['side'] = side
            if state:
                params['state'] = state
            if order_type:
                params['type'] = order_type
            if limit:
                params['limit'] = limit
            if created_at_start:
                params['created_at_start'] = created_at_start
            if created_at_end:
                params['created_at_end'] = created_at_end
            if updated_at_start:
                params['updated_at_start'] = updated_at_start
            if updated_at_end:
                params['updated_at_end'] = updated_at_end
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{self.ORDERS_ENDPOINT}?{query_string}" if query_string else self.ORDERS_ENDPOINT
            
            return self._make_request('GET', endpoint)
        except Exception as e:
            self.logger.error(f"Error getting orders: {str(e)}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an open crypto trading order.
        
        Args:
            order_id: The order ID to cancel
        """
        try:
            endpoint = f"{self.ORDERS_ENDPOINT}{order_id}/cancel/"
            response = self._make_request('POST', endpoint)
            return response is not None
        except Exception as e:
            self.logger.error(f"Error canceling order {order_id}: {str(e)}")
            return False

    def place_limit_order(self, symbol: str, side: str, asset_quantity: str, limit_price: str, time_in_force: str = "gtc") -> Optional[Dict]:
        """
        Place a limit order for crypto trading.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC-USD')
            side: 'buy' or 'sell'
            asset_quantity: Quantity of the asset to trade
            limit_price: Limit price for the order
            time_in_force: 'gtc' (good till canceled) or 'ioc' (immediate or cancel)
        """
        try:
            import uuid
            order_data = {
                "client_order_id": str(uuid.uuid4()),
                "symbol": symbol.upper(),
                "side": side,
                "type": "limit",
                "limit_order_config": {
                    "asset_quantity": self._round_asset_quantity(asset_quantity),
                    "limit_price": str(limit_price),
                    "time_in_force": time_in_force
                }
            }
            self.logger.info(f"Placing limit {side} order: {asset_quantity} {symbol} at ${limit_price}")
            return self._make_request('POST', self.ORDERS_ENDPOINT, json=order_data)
        except Exception as e:
            self.logger.error(f"Error placing limit order: {str(e)}")
            return None

    def place_stop_loss_order(self, symbol: str, side: str, asset_quantity: str, stop_price: str, time_in_force: str = "gtc") -> Optional[Dict]:
        """
        Place a stop loss order for crypto trading.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC-USD')
            side: 'buy' or 'sell'
            asset_quantity: Quantity of the asset to trade
            stop_price: Stop price that triggers the order
            time_in_force: 'gtc' (good till canceled) or 'ioc' (immediate or cancel)
        """
        try:
            import uuid
            order_data = {
                "client_order_id": str(uuid.uuid4()),
                "symbol": symbol.upper(),
                "side": side,
                "type": "stop_loss",
                "stop_loss_order_config": {
                    "asset_quantity": self._round_asset_quantity(asset_quantity),
                    "stop_price": str(stop_price),
                    "time_in_force": time_in_force
                }
            }
            self.logger.info(f"Placing stop loss {side} order: {asset_quantity} {symbol} at stop price ${stop_price}")
            return self._make_request('POST', self.ORDERS_ENDPOINT, json=order_data)
        except Exception as e:
            self.logger.error(f"Error placing stop loss order: {str(e)}")
            return None

    def place_stop_limit_order(self, symbol: str, side: str, asset_quantity: str, limit_price: str, stop_price: str, time_in_force: str = "gtc") -> Optional[Dict]:
        """
        Place a stop limit order for crypto trading.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC-USD')
            side: 'buy' or 'sell'
            asset_quantity: Quantity of the asset to trade
            limit_price: Limit price for the order
            stop_price: Stop price that triggers the order
            time_in_force: 'gtc' (good till canceled) or 'ioc' (immediate or cancel)
        """
        try:
            import uuid
            order_data = {
                "client_order_id": str(uuid.uuid4()),
                "symbol": symbol.upper(),
                "side": side,
                "type": "stop_limit",
                "stop_limit_order_config": {
                    "asset_quantity": self._round_asset_quantity(asset_quantity),
                    "limit_price": str(limit_price),
                    "stop_price": str(stop_price),
                    "time_in_force": time_in_force
                }
            }
            self.logger.info(f"Placing stop limit {side} order: {asset_quantity} {symbol} at limit ${limit_price}, stop ${stop_price}")
            return self._make_request('POST', self.ORDERS_ENDPOINT, json=order_data)
        except Exception as e:
            self.logger.error(f"Error placing stop limit order: {str(e)}")
            return None 