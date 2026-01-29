## API Client Usage

The API client in `src/api/robinhood_client.py` wraps Robinhood crypto endpoints and handles:
- Request signing (Ed25519)
- Rate limiting
- Retries with backoff
- Circuit breaker protection

### Example
```python
from src.api.robinhood_client import RobinhoodClient

client = RobinhoodClient()
client.authenticate()

# Market order
client.place_market_buy_order("BTC-USD", "25")

# Limit order
client.place_limit_order("BTC-USD", "buy", "0.001", "50000")
```

### Configuration

Local configuration lives in:
```
~/.robinhood_trading/config.json
```

Key settings:
- `api_timeout`
- `retry_max`
- `retry_backoff_base`
- `retry_backoff_max`
- `rate_limit_per_minute`
- `circuit_breaker_threshold`
- `circuit_breaker_timeout`
