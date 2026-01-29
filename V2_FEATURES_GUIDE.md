# 🚀 Robinhood Trading CLI V2 - What's New!

Hey there! 👋 If you've been using the basic version of this Robinhood trading tool, you're in for a treat. We've added some seriously cool new features that make this more than just a simple CLI tool - it's now a full-featured crypto trading platform!

**Built with ❤️ by Sachin Chhetri**

---

## 🎯 What's New in V2?

Think of V2 as your personal crypto trading assistant that never sleeps. We've added:

- 🤖 **Automated Trading Strategies** - Set it and forget it!
- 📊 **Smart Portfolio Analysis** - Know what's working and what's not
- 🔍 **Advanced Order Management** - Find and manage orders like a pro
- 🛡️ **Smart Validation** - No more "insufficient funds" surprises
- 📈 **Complete API Coverage** - Every Robinhood feature at your fingertips

---

## 🤖 Automated Trading - The Game Changer

### What is Automated Trading?

Imagine having a trading assistant that works 24/7, monitoring your positions and making smart decisions based on your rules. That's exactly what we've built!

### Stop Loss with Profit Taking

**What it does:** Automatically protects your profits and limits your losses.

**Real-world example:** You buy Bitcoin at $50,000 and set a 5% stop loss. If Bitcoin drops to $47,500, it automatically sells to protect your money. If it rises to $55,000, it sells to lock in your 10% profit.

```bash
# Set up automatic protection for your Bitcoin
python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 15.0

# What this means:
# - If price drops 5% from your entry, it sells (stop loss)
# - If price rises 15% from your entry, it sells (profit taking)
# - Uses $100 by default for the position
```

**Customize it:**
```bash
# More conservative: 3% stop loss, 20% profit target, $200 position
python main.py stop-loss-strategy ETH --stop-loss 3.0 --profit-target 20.0 --position-size 200

# More aggressive: 10% stop loss, 8% profit target, $50 position
python main.py stop-loss-strategy DOGE --stop-loss 10.0 --profit-target 8.0 --position-size 50
```

### Dollar-Cost Averaging (DCA)

**What it does:** Buys the same amount regularly, regardless of price. This is one of the smartest ways to invest in crypto!

**Why it works:** When prices are high, you buy fewer coins. When prices are low, you buy more coins. Over time, this averages out to a good price.

```bash
# Buy $50 worth of Bitcoin every 7 days
python main.py dca-strategy BTC --amount 50 --frequency 7

# What this means:
# - Every 7 days, automatically buy $50 worth of Bitcoin
# - No matter if Bitcoin is $40,000 or $60,000
# - Stops after 12 purchases (about 3 months)
```

**Customize your DCA:**
```bash
# More frequent, smaller amounts
python main.py dca-strategy ETH --amount 25 --frequency 3 --max-purchases 24

# Less frequent, larger amounts
python main.py dca-strategy BTC --amount 100 --frequency 14 --max-purchases 6
```

### Starting Your Automated Trading

Once you've set up your strategies, start the automated trading bot:

```bash
# Start all your configured strategies
python main.py auto-trade
```

**What happens:**
- The bot starts monitoring your positions
- It checks prices every minute
- When conditions are met, it automatically places trades
- You can stop it anytime with Ctrl+C

**Pro tip:** Start with small amounts to test the system before scaling up!

---

## 📊 Smart Portfolio Analysis

### Portfolio Performance - Know Your Winners and Losers

Ever wondered which of your crypto investments are doing well and which ones are dragging you down? Now you can see it at a glance!

```bash
# See your best and worst performing cryptos
python main.py portfolio-performance
```

**What you'll see:**
- 🏆 **Top 3 performers** - Your best investments
- 📉 **Bottom 3 performers** - Areas that might need attention
- 📈 **Performance percentages** - How much each crypto has gained or lost

### Quick Buying Power Check

Before placing a trade, quickly check how much money you have available:

```bash
# Check your available funds
python main.py buying-power
```

**Smart validation:** The system now checks your buying power before placing orders, so you won't get those annoying "insufficient funds" errors anymore!

---

## 🔍 Advanced Order Management

### Find Exactly What You're Looking For

The new order management system is like having a super-powered search for your trading history.

**View all your orders:**
```bash
python main.py orders
```

**Find specific orders:**
```bash
# Only open orders
python main.py orders --state open

# Only buy orders for Bitcoin
python main.py orders --symbol BTC-USD --side buy

# Only filled orders (completed trades)
python main.py orders --state filled

# Only market orders
python main.py orders --type market

# Combine filters - open buy orders for Bitcoin
python main.py orders --symbol BTC-USD --state open --side buy

# Limit results to 5 orders
python main.py orders --limit 5
```

### Cancel Orders Like a Pro

Found an order you want to cancel? No problem!

```bash
# Cancel an order by its ID
python main.py cancel 12345678-1234-1234-1234-123456789012
```

**How to find order IDs:**
1. Run `python main.py orders --state open`
2. Copy the ID from the first column
3. Use that ID with the cancel command

---

## 🔍 Discover Trading Pairs

### See What's Available to Trade

Not sure what cryptos you can trade? Now you can explore all available options:

```bash
# See all available trading pairs
python main.py trading-pairs

# Check specific pairs
python main.py trading-pairs BTC-USD ETH-USD DOGE-USD
```

**What you'll see:**
- 📊 **Symbol** - The trading pair (like BTC-USD)
- ✅ **Status** - Whether it's active for trading
- 🔍 **Easy discovery** - Find new cryptos to explore

---

## 🛡️ Smart Validation & Error Prevention

### No More Surprises!

We've made the system much smarter about preventing errors:

**Before placing a buy order:**
- ✅ Checks your buying power
- ✅ Validates the symbol exists
- ✅ Ensures the amount is reasonable
- ✅ Provides helpful error messages

**Example of smart error handling:**
```bash
# If you try to buy more than you can afford
python main.py buy BTC 10000

# You'll get a helpful message like:
# ❌ Insufficient buying power. You have $500 available.
# 💡 Try a smaller amount or check your buying power with:
#    python main.py buying-power
```

### Better Symbol Handling

The system now automatically handles symbol formatting:

```bash
# These all work the same way:
python main.py prices BTC
python main.py prices BTC-USD
python main.py buy ETH 50
python main.py buy ETH-USD 50
```

---

## 🎯 Real-World Usage Examples

### Scenario 1: The Conservative Investor

Sarah wants to invest in crypto but is worried about volatility:

```bash
# Set up conservative automated trading
python main.py stop-loss-strategy BTC --stop-loss 3.0 --profit-target 20.0 --position-size 100
python main.py dca-strategy ETH --amount 50 --frequency 14 --max-purchases 12

# Start automated trading
python main.py auto-trade
```

**What this does:**
- Protects against 3% losses
- Takes profits at 20% gains
- Buys $50 of Ethereum every 2 weeks
- Very conservative approach

### Scenario 2: The Active Trader

Mike likes to be more hands-on and wants better tools:

```bash
# Check current prices
python main.py prices BTC ETH DOGE ADA SOL

# See portfolio performance
python main.py portfolio-performance

# Find open orders
python main.py orders --state open

# Place a trade
python main.py buy BTC 100

# Monitor the order
python main.py orders --symbol BTC-USD --state open
```

### Scenario 3: The DCA Enthusiast

Alex believes in dollar-cost averaging and wants to automate it:

```bash
# Set up aggressive DCA for multiple cryptos
python main.py dca-strategy BTC --amount 100 --frequency 7 --max-purchases 52
python main.py dca-strategy ETH --amount 75 --frequency 7 --max-purchases 52
python main.py dca-strategy DOGE --amount 25 --frequency 7 --max-purchases 52

# Start the automated system
python main.py auto-trade
```

**What this does:**
- Buys $100 Bitcoin every week for a year
- Buys $75 Ethereum every week for a year
- Buys $25 Dogecoin every week for a year
- Total weekly investment: $200

---

## 🚨 Important Safety Information

### ⚠️ Automated Trading Risks

**Before using automated trading, understand these risks:**

- **Real Money**: Automated strategies trade with real funds
- **Market Risk**: Crypto prices are highly volatile
- **Technical Risk**: Internet issues or API failures can affect trading
- **Strategy Risk**: No strategy guarantees profits; losses are possible
- **24/7 Markets**: Crypto trades 24/7, strategies may execute at any time

### 🛡️ Safety Best Practices

1. **Start Small**: Begin with $10-50 trades to test the system
2. **Monitor Closely**: Check your orders and portfolio regularly
3. **Use Stop Losses**: Always have protection against large losses
4. **Don't Overinvest**: Only trade what you can afford to lose
5. **Test First**: Use small amounts to verify everything works

### 🎯 Recommended Testing Sequence

```bash
# 1. Test basic functionality
python main.py portfolio
python main.py prices BTC ETH

# 2. Test order management
python main.py orders
python main.py orders --state open

# 3. Test small buy order (if you have funds)
python main.py buy BTC 5

# 4. Test portfolio performance
python main.py portfolio-performance

# 5. Set up automated strategy with small amounts
python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 10.0 --position-size 10

# 6. Test automated trading briefly
python main.py auto-trade
# (Press Ctrl+C after a few minutes to stop)
```

---

## 🎉 Getting Started with V2 Features

### Quick Start for New Features

1. **Explore your portfolio:**
   ```bash
   python main.py portfolio-performance
   ```

2. **Check available trading pairs:**
   ```bash
   python main.py trading-pairs
   ```

3. **Set up your first automated strategy:**
   ```bash
   python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 15.0
   ```

4. **Start automated trading:**
   ```bash
   python main.py auto-trade
   ```

### Pro Tips for V2

- **Monitor your strategies**: Check portfolio performance regularly
- **Start conservative**: Use small amounts and tight stop losses initially
- **Combine strategies**: Use both stop loss and DCA for diversification
- **Keep learning**: Monitor which strategies work best for you

---

## 🔧 Troubleshooting V2 Features

### Common Issues with New Features

**❌ "No strategies configured" error:**
```bash
# Set up a strategy first
python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 10.0
```

**❌ Automated trading not working:**
```bash
# Check if strategies are configured
python main.py auto-trade

# If no strategies, set them up first
python main.py stop-loss-strategy BTC --stop-loss 5.0 --profit-target 10.0
```

**❌ Can't find trading pairs:**
```bash
# Check all available pairs
python main.py trading-pairs

# Look for the specific pair you want
python main.py trading-pairs BTC-USD ETH-USD
```

### Getting Help

- **Use debug mode**: `python main.py --debug <command>`
- **Check the logs**: Look for error messages
- **Test with small amounts**: Start with $5-10 trades
- **Verify your setup**: Make sure your API credentials are correct

---

## 🎯 What's Next?

The V2 features transform this from a simple CLI tool into a comprehensive crypto trading platform. You can now:

- ✅ **Automate your trading** with smart strategies
- ✅ **Analyze your portfolio** performance
- ✅ **Manage orders** like a professional trader
- ✅ **Discover new opportunities** with trading pairs
- ✅ **Trade with confidence** thanks to smart validation

**Ready to take your crypto trading to the next level?** 🚀

Start with the automated trading features and see how they can work for you. Remember to start small, monitor closely, and always trade responsibly!

---

*Happy automated trading! 🤖📈*

---

## Standalone Executable

You can create a double-clickable trading shell using PyInstaller:

```bash
python scripts/build_executable.py
./dist/RobinhoodTradingCLI
```

Keep your `.env` file in the folder where you run the executable.

---

**Need help?** Check the main README.md for basic setup instructions, or use the troubleshooting section above for V2-specific issues.  