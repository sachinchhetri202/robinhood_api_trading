# Robinhood Crypto Trading CLI

A beginner-friendly command-line tool to view your crypto portfolio, check prices, and trade on Robinhood—right from your terminal.

**Built by Sachin Chhetri**

> **🎯 Perfect for:** Crypto traders who want to manage their Robinhood portfolio from the command line without opening a web browser.

---

## What is this?

This project lets you:
- See your crypto holdings and buying power
- Check real-time prices for any coin
- View available trading pairs
- Place buy and sell orders (market, limit, stop loss, stop limit)
- View order history and manage open orders
- Cancel open orders
- All from a simple, secure command-line interface

No web browser needed!

---

## 🚀 Quick Start (5 minutes)

1. **Clone this repo**
   ```bash
   git clone <your-repo-url>
   cd Robinhood_API_Trading
   ```

2. **Set up Python environment** (see detailed instructions below)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Add your Robinhood API credentials** to a `.env` file
   ```bash
   # Create .env file with your credentials
   echo "API_KEY=your_api_key" > .env
   echo "BASE64_PRIVATE_KEY=your_base64_encoded_private_key" >> .env
   ```

4. **Test your setup:**
   ```bash
   python main.py portfolio
   ```

> **💡 First time?** Start with `python main.py --help` to see all available commands!

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- Robinhood account with crypto trading enabled
- Robinhood API credentials

### Step-by-Step Setup

1. **Create a virtual environment** (keeps your system Python clean):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python main.py --help
   ```

---

## ⚙️ Configuration

### Getting Your Robinhood API Credentials

1. **Enable API access** in your Robinhood account settings
2. **Generate API key and private key** from Robinhood developer portal
3. **Keep them secure** - never share or commit to version control

### Create Your .env File

Create a `.env` file in the project folder with your credentials:

```bash
# Create .env file
touch .env
```

Add your credentials to the `.env` file:
```
API_KEY=your_api_key_here
BASE64_PRIVATE_KEY=your_base64_encoded_private_key_here
ROBINHOOD_API_BASE_URL=https://trading.robinhood.com
```

> **🔒 Security Note:** Never share your `.env` file or commit it to version control. It's already in `.gitignore` for safety.

> **📚 Need help?** [See Robinhood API docs for credential setup details.](https://docs.robinhood.com/crypto/trading/)

---

## 🎯 Complete Command Reference

### 🆘 Getting Help
```bash
# See all available commands
python main.py --help

# Run any command with debug output
python main.py --debug portfolio
```

### 📊 Portfolio & Holdings
```bash
# View your complete portfolio with holdings and buying power
python main.py portfolio

# Show portfolio performance (best/worst performers)
python main.py portfolio-performance
```

### 💰 Price Checking
```bash
# Check single crypto price
python main.py prices BTC

# Check multiple crypto prices
python main.py prices BTC ETH DOGE ADA SOL

# Check with full symbol names
python main.py prices BTC-USD ETH-USD
```

### 🔄 Trading Pairs
```bash
# View all available trading pairs
python main.py trading-pairs

# View specific trading pairs
python main.py trading-pairs BTC-USD ETH-USD DOGE-USD
```

### 📋 Order Management
```bash
# View all your orders
python main.py orders

# View orders for specific crypto
python main.py orders --symbol BTC-USD

# View only open orders
python main.py orders --state open

# View only filled orders
python main.py orders --state filled

# View only buy orders
python main.py orders --side buy

# View only sell orders
python main.py orders --side sell

# View only market orders
python main.py orders --type market

# View only limit orders
python main.py orders --type limit

# Limit results to 5 orders
python main.py orders --limit 5

# Combine filters
python main.py orders --symbol BTC-USD --state open --side buy
```

### 💰 Buying Power
```bash
# Check your current buying power
python main.py buying-power
```

### 🛒 Trading (Buy/Sell)
```bash
# Buy $10 worth of Bitcoin
python main.py buy BTC 10

# Buy $25 worth of Ethereum
python main.py buy ETH 25

# Buy $5 worth of Dogecoin
python main.py buy DOGE 5

# Sell $10 worth of Bitcoin (if you have holdings)
python main.py sell BTC 10

# Sell $15 worth of Ethereum (if you have holdings)
python main.py sell ETH 15
```

> **💡 Smart Validation**: The app now checks your buying power before placing orders and provides helpful error messages if you don't have enough funds.

### ❌ Order Cancellation
```bash
# Cancel an order by ID (replace with actual order ID)
python main.py cancel 12345678-1234-1234-1234-123456789012
```

### 🤖 Automated Trading Strategies

#### Stop Loss with Profit Taking
```bash
# Set up stop loss strategy (5% stop loss, 10% profit target)
python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 15.0

# Custom configuration
python main.py stop-loss-strategy ETH --stop-loss 3.0 --profit-target 20.0 --position-size 200
```

#### Dollar-Cost Averaging (DCA)
```bash
# Set up DCA strategy (buy $50 every 7 days)
python main.py dca-strategy BTC --amount 50 --frequency 7

# Custom DCA configuration
python main.py dca-strategy ETH --amount 25 --frequency 14 --max-purchases 24
```

#### Start Automated Trading
```bash
# Start all configured strategies
python main.py auto-trade
```

> **⚠️ Important**: Automated trading involves real money. Test with small amounts first and monitor closely.

### 🚨 Automated Trading Risks

**Before using automated trading, understand these risks:**

- **Real Money**: Automated strategies trade with real funds
- **Market Risk**: Crypto prices are highly volatile
- **Technical Risk**: Internet issues, API failures, or bugs can affect trading
- **Strategy Risk**: No strategy guarantees profits; losses are possible
- **24/7 Markets**: Crypto trades 24/7, strategies may execute at any time

**Best Practices:**
- Start with small amounts ($10-50)
- Test strategies thoroughly before scaling up
- Monitor automated trading regularly
- Have stop-losses in place
- Don't invest more than you can afford to lose

---

## 🧪 Testing Your Setup

### First-Time User Testing Sequence
```bash
# 1. Test basic functionality
python main.py --help
python main.py portfolio
python main.py prices BTC ETH

# 2. Test trading pairs
python main.py trading-pairs
python main.py trading-pairs BTC-USD ETH-USD

# 3. Test order management
python main.py orders
python main.py orders --state open
python main.py orders --limit 3

# 4. Test small buy order (if you have funds)
python main.py buy BTC 5

# 5. Check order was created
python main.py orders --state open

# 6. Test portfolio performance
python main.py portfolio-performance
```

### 🐛 Error Testing
```bash
# Test invalid symbol
python main.py prices INVALID

# Test invalid amount
python main.py buy BTC -5

# Test without authentication (remove .env file temporarily)
python main.py portfolio
```

---

## 🔧 Advanced Usage

### API-Only Features

The following order types are available through the API client but not yet exposed via CLI:

- **Limit Orders**: Place orders at specific prices
- **Stop Loss Orders**: Automatic sell when price drops to a certain level
- **Stop Limit Orders**: Stop loss with a limit price

Example API usage:
```python
from src.api.robinhood_client import RobinhoodClient

client = RobinhoodClient()
client.authenticate()

# Place a limit buy order
client.place_limit_order("BTC-USD", "buy", "0.001", "50000")

# Place a stop loss order
client.place_stop_loss_order("BTC-USD", "sell", "0.001", "45000")
```

### 🤖 Automated Trading Strategies

The app now includes automated trading strategies that can run continuously:

#### **Stop Loss with Profit Taking**
- **Purpose**: Automatically sell when price drops (stop loss) or rises (profit taking)
- **How it works**: Monitors position and sells when stop loss or profit target is hit
- **Use case**: Protect against losses while capturing gains

#### **Dollar-Cost Averaging (DCA)**
- **Purpose**: Buy fixed amounts at regular intervals regardless of price
- **How it works**: Automatically purchases set amount on schedule
- **Use case**: Reduce impact of price volatility over time

#### **Trailing Stop Loss** (Coming Soon)
- **Purpose**: Dynamic stop loss that moves up as price increases
- **How it works**: Adjusts stop loss level as position gains value
- **Use case**: Lock in profits while allowing for upside

#### **Portfolio Rebalancing** (Coming Soon)
- **Purpose**: Maintain target allocation percentages
- **How it works**: Automatically buys/sells to maintain desired ratios
- **Use case**: Maintain diversified portfolio over time

---

## 🚨 Troubleshooting & Common Issues

### Quick Fixes

**❌ Authentication failed?**
```bash
# Check your .env file exists and has correct format
cat .env

# Verify your credentials are correct
python main.py --debug portfolio
```

**❌ Command not found?**
```bash
# Make sure you're in the right folder
pwd
ls -la

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**❌ "asset_quantity must be specified" error?**
- ✅ **Fixed!** This was a bug in market buy orders that has been resolved
- The app now automatically calculates asset quantity from USD amount

**❌ "must have at most 18 decimal places" error?**
- ✅ **Fixed!** Asset quantities are now properly rounded to 8 decimal places
- This prevents Robinhood's decimal place limit errors

**❌ No holdings found?**
- Make sure your Robinhood account has crypto trading enabled
- You need existing holdings to test sell orders

**❌ Order cancellation failed?**
- Verify the order ID is correct and the order is still open
- Use `python main.py orders --state open` to see current open orders

**❌ "Insufficient buying power" error?**
- Check your current buying power: `python main.py buying-power`
- Try a smaller amount that fits within your available funds
- The app now validates buying power before placing orders

### Getting Help

1. **Check the logs** with debug mode:
   ```bash
   python main.py --debug portfolio
   ```

2. **Verify your setup**:
   ```bash
   python main.py --help
   ```

3. **Test with small amounts** first:
   ```bash
   python main.py buy BTC 5
   ```

---

## Troubleshooting

- **Authentication failed?**
  - Double-check your `.env` file and API credentials.
  - Make sure your account is enabled for crypto trading.
- **Command not found?**
  - Make sure you’re in the right folder and your virtual environment is activated.

---

## Testing

Run all tests:
```bash
pytest
```
Run with coverage:
```bash
pytest --cov=src tests/
```

---

## Recent Updates

### ✅ Fixed Issues
- **Market Buy Orders**: Fixed the "asset_quantity must be specified" error by calculating asset quantity from current price
- **Complete API Coverage**: Added all missing Robinhood crypto trading endpoints

### 🆕 New Features
- **Trading Pairs**: View available crypto trading pairs
- **Order History**: Complete order management with filtering
- **Order Cancellation**: Cancel open orders by ID
- **Advanced Order Types**: Support for limit, stop loss, and stop limit orders
- **Enhanced CLI**: New commands for better trading workflow
- **Smart Buying Power Validation**: Check funds before placing orders
- **Buying Power Command**: Quick check of available funds

## Security

- Never share your `.env` file or private key.
- Use a virtual environment for safety.

---

## Complete Feature Coverage

This CLI now supports **all** Robinhood crypto trading API endpoints:

| Feature | Status | CLI Command |
|---------|--------|-------------|
| ✅ Get Trading Pairs | Complete | `trading-pairs` |
| ✅ Get Holdings | Complete | `portfolio` |
| ✅ Get Orders | Complete | `orders` |
| ✅ Get Buying Power | Complete | `buying-power` |
| ✅ Place Market Orders | Complete | `buy`, `sell` |
| ✅ Place Limit Orders | Complete | API only |
| ✅ Place Stop Loss Orders | Complete | API only |
| ✅ Place Stop Limit Orders | Complete | API only |
| ✅ Cancel Orders | Complete | `cancel` |
| ✅ Authentication | Complete | All commands |
| ✅ Price Data | Complete | `prices` |
| ✅ Smart Validation | Complete | Auto-check buying power |
| ✅ Stop Loss Strategy | Complete | `stop-loss-strategy` |
| ✅ DCA Strategy | Complete | `dca-strategy` |
| ✅ Automated Trading | Complete | `auto-trade` |

## 🎉 You're All Set!

### What's Next?

1. **Start with the basics**:
   ```bash
   python main.py portfolio
   python main.py prices BTC ETH
   ```

2. **Explore trading pairs**:
   ```bash
   python main.py trading-pairs
   ```

3. **Try a small trade** (if you have funds):
   ```bash
   python main.py buy BTC 5
   ```

4. **Monitor your orders**:
   ```bash
   python main.py orders --state open
   ```

### Pro Tips

- **Use debug mode** when troubleshooting: `python main.py --debug <command>`
- **Start small** with trades to test the system
- **Check order status** regularly with the orders command
- **Keep your API credentials secure** and never share them

### Need More Help?

- Check the troubleshooting section above
- Use debug mode to see detailed logs
- Test with small amounts first
- Make sure your Robinhood account has crypto trading enabled

## License

MIT

---

*Happy trading! 🚀* 