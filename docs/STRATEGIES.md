## Automated Strategies

### Stop Loss with Profit Taking
- Tracks entry price on first purchase
- Sells if price drops below stop-loss threshold
- Sells if price reaches profit target

### Dollar-Cost Averaging (DCA)
- Executes purchases on a fixed schedule
- Tracks last purchase time and count
- Respects `max_purchases`

### Persistence

Strategies are stored in:
```
~/.robinhood_trading/strategies.json
```

State (entry prices, DCA counters) is stored in:
```
~/.robinhood_trading/state.json
```

### Strategy Management Commands
```bash
python main.py list-strategies
python main.py load-strategies
python main.py remove-strategy stop_loss_BTC-USD
```
