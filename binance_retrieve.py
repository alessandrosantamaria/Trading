import requests
import json
from datetime import datetime
from decimal import Decimal

import constraints
from telegram_message import send_message_crypto, send_message_target_achieved

base_url = "https://api.binance.com/api/v3"

SYMBOL_USDT = ['1INCH', 'AAVE', 'ADA', 'ALGO', 'ARPA', 'AR', 'ATOM', 'AVAX', 'AXS', 'BAL', 'BAT', 'BNB', 'BCH', 'BTC',
               'CAKE', 'CELO', 'CHR', 'CHZ', 'COMP', 'CRV', 'DASH', 'DOGE', 'DOT', 'EGLD', 'ENJ', 'EOS', 'ETC', 'ETH',
               'FIL', 'FLM',
               'FLOW', 'FTM', 'FTT', 'GALA', 'GNO', 'GRT', 'HBAR', 'HOT', 'ICP', 'ICX', 'IOTA', 'KSM', 'LINK', 'LPT',
               'LRC', 'LTC',
               'MANA', 'MATIC', 'OMG', 'ONE', 'QNT', 'RUNE', 'SAND', 'SHIB', 'SOL', 'SUSHI', 'THETA', 'UNI', 'VET',
               'WAVES', 'XEC',
               'XEM', 'XRP', 'ZIL']


def get_historical_price(symbol: str, currency: str, interval: str, limit: int):
    r = requests.get(
        f'{base_url}/klines?symbol={symbol}{currency}&interval={interval}&limit={limit}')
    content = json.loads(r.content)
    list_candles = []
    if (len(content) > 0 and type(content) is list):
        for x in content:
            dict = {
                'symbol': symbol,
                'currency': currency,
                'high': x[2],
                'close': x[4],
                'timestamp': datetime.fromtimestamp(x[6] / 1000.0)
            }
            list_candles.append(dict)

    return list_candles


def backtest_percentage(percentage_input, limit, interval):
    all_count_win = 0
    all_count_lose = 0
    url = 'https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    params = {
        'limit': 100,
    }
    r = requests.get(url, params=params)
    data = r.json()
    for symbol in data['data']:

        arr = get_historical_price(symbol=symbol['symbol'], currency='BUSD', interval=interval, limit=limit)
        count_win = 0
        count_lose = 0
        found = False

        for idx, x in enumerate(arr):
            if idx != 0:
                percentage = (float(x['close']) - float(arr[idx - 1]['close'])) / float(arr[idx - 1]['close']) * 100
                initial_price = float(x['close'])
                timestamp = str(x['timestamp'])
                if percentage > percentage_input:
                    sub_array = arr[idx + 1: len(arr)]
                    for sub in sub_array:
                        percentage_recall = (float(sub['high']) - initial_price) / initial_price * 100
                        if percentage_recall > percentage_input:
                            count_win += 1
                            found = True
                            print(
                                'Order opened {} with price {} for symbol {}{} close at {} at price {} with percentage earned {}'.format(
                                    timestamp, initial_price, sub['symbol'], sub['currency'], str(sub['timestamp']),
                                    sub['high'],
                                    percentage_recall))
                            all_count_win += 1
                            break
                    if found == False:
                        count_lose += 1
                        print(
                            'Order opened {} with price {} for symbol {}{} is a loss trade'.format(timestamp,
                                                                                                   initial_price,
                                                                                                   sub['symbol'],
                                                                                                   sub['currency']))
                        all_count_lose += 1
        print('Win Trades {} - Lose Trades {}'.format(count_win, count_lose))
    print('All count Win {} - All count Lose {}'.format(all_count_win, all_count_lose))


def signal_crypto_percentage(percentage, interval):
    url = 'https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    params = {
        'limit': 100,
    }
    r = requests.get(url, params=params)
    data = r.json()
    for symbol in data['data']:

        arr = get_historical_price(symbol=symbol['symbol'], currency='BUSD', interval=interval, limit=3)
        if len(arr)>0:
           percentage_calc = (float(arr[1]['close']) - float(arr[0]['close'])) / float(arr[0]['close']) * 100
           print("Symbol {}: Actual Price : {} Previous Price : {} Percentage {}".format(symbol['symbol'],
                                                                                         float(arr[1]['close']),
                                                                                         float(arr[0]['close']),
                                                                                         percentage_calc))
           if percentage_calc > percentage:
               send_message_crypto('{}{}'.format(arr[1]['symbol'], arr[1]['currency']), arr[1]['close'])


def retrieve_price_crypto(symbol, target):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {}
    url = 'https://api.binance.com/api/v3/ticker/price?symbol={}{}'
    response = requests.request("GET", url.format(symbol, 'USDT'), headers=headers, data=payload)
    tickers = json.loads(response.text)
    if Decimal(tickers['price']) > Decimal(target) and constraints.message_already_send == False:
        send_message_target_achieved('{}{}'.format(symbol, 'USDT'), target)
        constraints.message_already_send = True


#backtest_percentage(5, 1000, '4h')
#signal_crypto_percentage(5,'4h')
