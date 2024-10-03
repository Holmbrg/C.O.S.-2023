import requests
import time
import json
from typing import Dict, Any, Optional

# Replace with your actual secret key
TAAPI_SECRET_KEY = "YOUR_SECRET_KEY"

def fetch_indicator_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetches indicator data for a given symbol from the TAAPI.io API.

    Args:
        symbol (str): The symbol to fetch data for.

    Returns:
        Optional[Dict[str, Any]]: The JSON response as a dictionary, or None if an error occurs.
    """
    url = "https://api.taapi.io/bulk"
    payload = {
        "secret": TAAPI_SECRET_KEY,
        "construct": {
            "exchange": "binancefutures",
            "symbol": f"{symbol}/USDT",
            "interval": "1h",
            "indicators": [
                {"indicator": "rsi"},
                {"indicator": "ema", "period": 200},
                {"indicator": "stochrsi"}
            ]
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {symbol}: {e}")
        return None

def get_current_price(symbol: str) -> Optional[float]:
    """
    Retrieves the current price of a symbol from the Binance API.

    Args:
        symbol (str): The symbol to get the price for.

    Returns:
        Optional[float]: The current price, or None if an error occurs.
    """
    symbol_pair = symbol.upper() + 'USDT'
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_pair}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except requests.exceptions.RequestException as e:
        print(f"Failed to get price for {symbol}: {e}")
        return None

def process_data(symbol: str, data: Dict[str, Any]) -> None:
    """
    Processes the indicator data and checks for trading opportunities.

    Args:
        symbol (str): The symbol being processed.
        data (Dict[str, Any]): The indicator data.
    """
    if 'data' not in data:
        print(f"{symbol} data not obtainable")
        return

    indicators = {}
    for item in data['data']:
        indicator = item.get('indicator')
        result = item.get('result', {})

        if indicator == 'rsi':
            indicators['rsi'] = result.get('value')
        elif indicator == 'stochrsi':
            indicators['stochrsi_fastk'] = result.get('valueFastK')
            indicators['stochrsi_fastd'] = result.get('valueFastD')
        elif indicator == 'ema':
            indicators['ema_200'] = result.get('value')

    price = get_current_price(symbol)
    if price is None:
        return

    ema_200 = indicators.get('ema_200')
    if ema_200 is None:
        print(f"EMA 200 not available for {symbol}")
        return

    ema_200_kvotient = (((price - ema_200) / ((price + ema_200) / 2)) * 100)

    rsi = indicators.get('rsi')
    stochrsi_fastk = indicators.get('stochrsi_fastk')
    stochrsi_fastd = indicators.get('stochrsi_fastd')

    if None in (rsi, stochrsi_fastk, stochrsi_fastd):
        print(f"Indicators not available for {symbol}")
        return

    # Downtrending conditions
    if (44 < rsi < 54 and 90 < stochrsi_fastk < 100 and
        80 < stochrsi_fastd < 100 and -0.19 < ema_200_kvotient < 0):
        print(f"Opportunity at: {symbol}")

    if (rsi > 60 and 90 < stochrsi_fastk < 100 and
        80 < stochrsi_fastd < 100 and -0.19 < ema_200_kvotient < 0):
        print(f"Opportunity at: {symbol}")

    if (rsi > 60 and 90 < stochrsi_fastk < 100 and
        80 < stochrsi_fastd < 100 and ema_200_kvotient < -0.35):
        print(f"Opportunity at: {symbol}")

    if (rsi > 60 and 90 < stochrsi_fastk < 100 and
        80 < stochrsi_fastd < 100 and 0.3 < ema_200_kvotient < 1):
        print(f"Opportunity at: {symbol}")

    # Uptrending conditions
    if (46 < rsi < 56 and 0 < stochrsi_fastk < 10 and
        0 < stochrsi_fastd < 20 and 0 < ema_200_kvotient < 0.19):
        print(f"Opportunity at: {symbol}")

    if (rsi < 40 and 0 < stochrsi_fastk < 10 and
        0 < stochrsi_fastd < 20 and ema_200_kvotient > 0.35):
        print(f"Opportunity at: {symbol}")

    if (rsi < 40 and 0 < stochrsi_fastk < 10 and
        0 < stochrsi_fastd < 20 and 0 < ema_200_kvotient < 0.19):
        print(f"Opportunity at: {symbol}")

    if (rsi < 40 and 0 < stochrsi_fastk < 10 and
        0 < stochrsi_fastd < 20 and -1 < ema_200_kvotient < -0.3):
        print(f"Opportunity at: {symbol}")

def process_symbol(symbol: str) -> None:
    """
    Fetches and processes data for a single symbol.

    Args:
        symbol (str): The symbol to process.
    """
    data = fetch_indicator_data(symbol)
    if data:
        process_data(symbol, data)

def main() -> None:
    """
    Main function to process all symbols in a loop.
    """
    symbols = [
        'BTC', 'ETH', 'XRP', 'LTC', 'BNB', 'ADA', 'BAT', 'ETC', 'XLM', 'ZRX', 'DOGE', 'PIXEL', 'JUP', 'ALT',
        'MANTA', 'XAI', '1000RATS', '1000SATS', 'JTO', 'PYTH', 'ORDI', 'MEME', 'TIA', 'BSV', 'BIGTIME', 'LOOM',
        'GLMR', 'CYBER', 'SEI', 'YGG', 'AGLD', 'ARKM', 'PENDLE', 'WLD', 'XVG', 'MDT', 'MAV', 'COMBO', 'KEY',
        'UMA', 'RAD', 'IDEX', 'EDU', 'XVS', 'HFT', 'RDNT', 'LEVER', 'ID', 'LQTY', 'TRU', 'CKB', 'SSV', 'ACH',
        'BNX', 'STX', 'CFX', 'GMX', 'AGIX', 'MINA', 'RNDR', 'MAGIC', 'HOOK', 'FRAX', 'CVX', 'LDO', 'LUN2',
        'DAR', 'JASMY', 'WOO', 'APE', 'GMT', 'IMX', 'PEOPLE', 'ENS', 'ARPA', 'KLAY', 'AR', 'CELO', '1000XEC',
        'DYDX', 'C98', 'AUDIO', 'IOTX', 'BAKE', 'NKN', 'HOT', 'DENT', 'CHR', 'COTI', 'SFP', 'UNFI', 'LIT',
        'GRT', 'ALPHA', 'AXS', 'CTK', 'BEL', 'RSR', 'FIL', 'AAVE', 'KSM', 'FLM', 'AVAX', 'RUNE', 'CRV', 'DOT',
        'SXP', 'OMG', 'TRX', 'BCH', 'ETC', 'ATOM', 'NEO', 'VET', 'QTUM', 'ONT', 'KNC', 'COMP', 'MKR', 'ONE',
        'BAND', 'STORJ', 'UNI', 'SOL', 'EGLD', 'ZEN', '1INCH', 'FTM', 'MATIC', 'MANA', 'ALGO', 'LINK', 'EOS',
        'ENJ', 'NEAR', 'SUSHI', 'LRC', 'LPT', 'SLP', 'CHZ', 'OGN', 'GALA', 'TLM', 'SNX', 'API3', 'BNT', 'FLOW',
        'GTC', 'THETA', 'OCEAN', 'CELR', 'SKL', 'WAXP', 'FET', 'ICP', 'OP', 'ROSE', 'RARE', 'ASTR', 'GAL',
        'SAND', 'QNT', 'STG', 'KAVA', 'APT', 'MASK', 'STMX', 'POLYX', 'IOST', 'ARB', 'FLOKI', 'BLUR', 'ANKR',
        'HBAR', 'ICX', 'IOTA', 'RVN', 'WAVES', 'XTZ', 'ZIL', 'ORBS', 'SUI', 'ZETA', 'ACE'
    ]

    while True:
        for symbol in symbols:
            process_symbol(symbol)
            time.sleep(15)  # Adjust based on your API rate limits
        print('All tokens tested. Restarting.')


if __name__ == "__main__":
    main()
