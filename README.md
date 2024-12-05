# Shoonya Trading Bot

## Overview
This is a simple automated trading bot designed to interact with the Shoonya broker platform. The bot can automatically log in, place orders, and execute trades based on configurable parameters.

## ⚠️ Disclaimer
**IMPORTANT: This is a personal project developed during college years and is NOT suitable for production use. Use at your own risk. The author is not responsible for any financial losses or trading mistakes.**

## Prerequisites
- Python 3.8+
- Shoonya broker account
- Necessary dependencies (see `requirements.txt`)

## Configuration

### API Configuration
```python
# API Endpoints
HOST = 'https://api.shoonya.com/NorenWClientTP/'
WEBSOCKET = 'wss://api.shoonya.com/NorenWSTP/'

# Broker Credentials
USER = 'xxxxxx'
PWD = 'xxxxxx'
TOTP_KEY = 'xxxxxx'
APP_KEY = 'xxxxxx'
IMEI = 'xxxxxx'
SHOONAY_OBJ = None

# Database Credentials
DB_HOST = "xxxxxxxx"
DB_NAME = "xxxxxxxxxxxx"
DB_USER = "xxxxxxxxx"
DB_PASSWORD = "xxxxxx@xxxxx"

# Logging Configuration
APPLICATION_STRING = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx12121dzxxxxxxx'

# Trading Configuration
LOGIN_TIME = '09:08'
ORDER_PLACEMENT_TIME = '09:29'
EXCH = 'NSE'
ENTRY = 'B'
EXIT = 'S'
INSTRUMENT = ['M&M-EQ', 'IDBI-EQ', 'KPITTECH-EQ', 'TATACONSUM-EQ', 'ADANIPORTS-EQ']
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shoonya-trading-bot.git
cd shoonya-trading-bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your credentials:
- Open the configuration file
- Replace placeholders with your actual Shoonya broker credentials
- Customize trading parameters as needed

## Usage
Run the bot using:
```bash
python main.py
```

## Features
- Automatic login at specified time
- Configurable trading strategy
- Flexible order placement
- Customizable trading logic

## Contribution
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License

Copyright (c) [Year] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Caution
- This is an experimental project
- Always test in a safe environment
- Monitor trades closely
- Do not use with real money without thorough testing
