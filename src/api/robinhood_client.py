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
from typing import Dict, Optional
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
        """
        try:
            import uuid
            order_data = {
                "client_order_id": str(uuid.uuid4()),
                "symbol": symbol.upper(),
                "side": "buy",
                "type": "market",
                "market_order_config": {
                    "quote_amount": str(quote_amount)
                }
            }
            self.logger.info(f"Placing market buy order: {symbol} for ${quote_amount}")
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
                    "asset_quantity": str(asset_quantity)
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