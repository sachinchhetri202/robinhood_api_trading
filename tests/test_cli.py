"""Tests for the CLI interface"""

import pytest
from click.testing import CliRunner
from decimal import Decimal
from unittest.mock import Mock, patch

from main import cli

# Sample test data
MOCK_HOLDINGS = {
    'results': [
        {
            'symbol': 'BTC-USD',
            'quantity': '0.5'
        },
        {
            'symbol': 'ETH-USD',
            'quantity': '2.0'
        }
    ]
}

MOCK_PRICES = {
    'BTC-USD': {'price': '50000.00'},
    'ETH-USD': {'price': '3000.00'}
}

@pytest.fixture
def mock_client():
    """Create a mock Robinhood client"""
    with patch('src.trading.trading_bot.RobinhoodClient') as mock:
        client = mock.return_value
        
        # Configure mock methods
        client.authenticate.return_value = True
        client.get_holdings.return_value = MOCK_HOLDINGS
        client.get_buying_power.return_value = 10000.00
        
        def mock_get_crypto_price(symbol):
            return {'price': MOCK_PRICES.get(symbol, {}).get('price', '0.00')}
        client.get_crypto_price.side_effect = mock_get_crypto_price
        
        client.place_market_buy_order.return_value = {'id': 'test-order-id'}
        client.place_market_sell_order.return_value = {'id': 'test-order-id'}
        
        yield client

@pytest.fixture
def runner():
    """Create a Click CLI test runner"""
    return CliRunner()

def test_portfolio_command(runner, mock_client):
    """Test the portfolio command"""
    result = runner.invoke(cli, ['portfolio'])
    assert result.exit_code == 0
    assert 'BTC-USD' in result.output
    assert 'ETH-USD' in result.output
    assert 'Buying Power: $10,000.00' in result.output

def test_prices_command(runner, mock_client):
    """Test the prices command"""
    result = runner.invoke(cli, ['prices', 'BTC-USD', 'ETH-USD'])
    assert result.exit_code == 0
    assert 'BTC-USD' in result.output
    assert '$50000.00' in result.output
    assert 'ETH-USD' in result.output
    assert '$3000.00' in result.output

def test_buy_command_success(runner, mock_client):
    """Test successful buy command"""
    result = runner.invoke(cli, ['buy', 'BTC-USD', '100'])
    assert result.exit_code == 0
    assert 'Buy order placed' in result.output
    assert 'test-order-id' in result.output
    mock_client.place_market_buy_order.assert_called_once_with(
        symbol='BTC-USD',
        quote_amount='100.0'
    )

def test_buy_command_invalid_amount(runner, mock_client):
    """Test buy command with invalid amount"""
    result = runner.invoke(cli, ['buy', 'BTC-USD', '-100'])
    assert result.exit_code == 2
    assert 'Invalid value for' in result.output or 'Error:' in result.output

def test_buy_command_invalid_symbol(runner, mock_client):
    """Test buy command with invalid symbol"""
    result = runner.invoke(cli, ['buy', 'invalid!symbol', '100'])
    assert result.exit_code == 1
    assert 'Error: Invalid symbol format' in result.output

def test_sell_command_success(runner, mock_client):
    """Test successful sell command"""
    result = runner.invoke(cli, ['sell', 'BTC-USD', '100'])
    assert result.exit_code == 0
    assert 'Sell order placed' in result.output
    assert 'test-order-id' in result.output

def test_sell_command_insufficient_balance(runner, mock_client):
    """Test sell command with insufficient balance"""
    # Mock holdings for this test
    mock_client.get_holdings.return_value = {
        'results': [
            {
                'symbol': 'BTC-USD',
                'quantity': '0.001'  # Very small amount
            }
        ]
    }
    
    result = runner.invoke(cli, ['sell', 'BTC-USD', '100000'])  # Try to sell more than we have
    assert result.exit_code == 1
    assert 'Insufficient BTC-USD balance' in result.output

def test_sell_command_no_holdings(runner, mock_client):
    """Test sell command with no holdings"""
    mock_client.get_holdings.return_value = {'results': []}
    result = runner.invoke(cli, ['sell', 'BTC-USD', '100'])
    assert result.exit_code == 1
    assert 'holdings found' in result.output

def test_authentication_failure(runner, mock_client):
    """Test command behavior when authentication fails"""
    mock_client.authenticate.return_value = False
    result = runner.invoke(cli, ['portfolio'])
    assert result.exit_code == 1
    assert 'Authentication failed' in result.output

def test_api_error(runner, mock_client):
    """Test command behavior when API call fails"""
    mock_client.get_holdings.side_effect = Exception("API Error")
    result = runner.invoke(cli, ['portfolio'])
    assert result.exit_code == 2
    assert 'Error: API Error' in result.output 