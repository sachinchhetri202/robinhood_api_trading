# Robinhood Crypto Trading CLI

A beginner-friendly command-line tool to view your crypto portfolio, check prices, and trade on Robinhood—right from your terminal.

**Built by Sachin Chhetri**

---

## What is this?

This project lets you:
- See your crypto holdings and buying power
- Check real-time prices for any coin
- Place buy and sell orders
- All from a simple, secure command-line interface

No web browser needed!

---

## Quick Start

1. **Clone this repo**
2. **Set up Python** (see below)
3. **Add your Robinhood API credentials** to a `.env` file
4. **Run your first command:**
   ```bash
   python main.py portfolio
   ```

---

## Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Create a `.env` file in the project folder with:
```
API_KEY=your_api_key
BASE64_PRIVATE_KEY=your_base64_encoded_private_key
ROBINHOOD_API_BASE_URL=https://trading.robinhood.com
```
> **Note:** You need a Robinhood API key and private key. [See Robinhood API docs for details.](https://docs.robinhood.com/crypto/trading/)

---

## Usage

- See all commands:
  ```bash
  python main.py --help
  ```
- View your portfolio:
  ```bash
  python main.py portfolio
  ```
- Check prices:
  ```bash
  python main.py prices BTC ETH DOGE
  ```
- Buy $100 of Bitcoin:
  ```bash
  python main.py buy BTC 100
  ```
- Sell $50 of Dogecoin:
  ```bash
  python main.py sell DOGE 50
  ```

- Show your best and worst performers:
  ```bash
  python main.py portfolio-performance
  ```
  This will show the top 3 and bottom 3 coins in your portfolio by current value, using only your Robinhood data (no external APIs).

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

## Security

- Never share your `.env` file or private key.
- Use a virtual environment for safety.

---

## License

MIT

---

*Happy trading!* 