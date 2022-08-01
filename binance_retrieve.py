import time

import requests
import json
from datetime import datetime,time
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


def export_history():
    start_time = 1609459200000
    end_time = 0
    one_day = 84000000
    end = int(datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).timestamp())*1000
    url = 'https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    params = {
        'limit': 100,
    }
    r = requests.get(url, params=params)
    data = r.json()
    all_data = []
    for symbol in data['data']:
        array_result = []
        final = []
        while end_time < end:

            end_time = start_time + (one_day*150)
            arr = get_historical_price_start_end(symbol=symbol['symbol'], currency='BUSD', interval='4h', limit=1000,
                                                 startDate=start_time, endDate=end_time)

            array_result.append(arr)
            start_time = end_time
        for x in array_result:
            final = final + x
        data = {
            symbol['symbol'] : final
        }
        all_data.append(data)
        start_time = 1609459200000
        end_time = 0
    return all_data

def read_file():
    with open('history.txt') as f:
        data = f.read()
        print()

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
                'timestamp': datetime.fromtimestamp(x[6] / 1000.0),
                'open': x[1],
                'low': x[3]
            }
            list_candles.append(dict)

    return list_candles


def get_historical_price_start_end(symbol: str, currency: str, interval: str, limit: int, startDate: int, endDate: int):
    r = requests.get(
        f'{base_url}/klines?symbol={symbol}{currency}&interval={interval}&limit={limit}&startTime={startDate}&endTime={endDate}')
    content = json.loads(r.content)
    list_candles = []
    if (len(content) > 0 and type(content) is list):
        for x in content:
            dict = {
                'symbol': symbol,
                'currency': currency,
                'high': x[2],
                'close': x[4],
                'timestamp': datetime.fromtimestamp(x[6] / 1000.0),
                'open': x[1],
                'low': x[3]
            }
            list_candles.append(dict)

    return list_candles





def backtest_percentage(percentage_input=2, limit=1000, interval='1h', print_bool=False):
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
                timestamp = x['timestamp']
                if percentage > percentage_input:
                    sub_array = arr[idx + 1: len(arr)]
                    for sub in sub_array:
                        percentage_recall = (float(sub['high']) - initial_price) / initial_price * 100
                        if percentage_recall > percentage_input:
                            count_win += 1
                            found = True
                            if print_bool == True:
                                print(
                                    'Order opened {} with price {} for symbol {}{} close at {} at price {} with percentage earned {} in {}'.format(
                                        str(timestamp), initial_price, sub['symbol'], sub['currency'],
                                        str(sub['timestamp']),
                                        sub['high'],
                                        percentage_recall, str(sub['timestamp'] - timestamp)))
                            all_count_win += 1
                            break

                    if found == False:
                        count_lose += 1
                        if print_bool == True:
                            print(
                                'Order opened {} with price {} for symbol {}{} is a loss trade'.format(str(timestamp),
                                                                                                       initial_price,
                                                                                                       sub['symbol'],
                                                                                                       sub['currency']))
                        all_count_lose += 1
        if len(arr) > 0:
            print('Win Trades {} - Lose Trades {} for symbol {}{}'.format(count_win, count_lose, x['symbol'],
                                                                          x['currency']))
    print('All count Win {} - All count Lose {}'.format(all_count_win, all_count_lose))


def backtest_percentage_slope(percentage_input, limit, interval):
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
            if idx > 4:
                percentage = (float(x['close']) - float(x['open'])) / float(x['open']) * 100
                percentage_1 = (float(arr[idx - 1]['close']) - float(arr[idx - 1]['open'])) / float(
                    arr[idx - 1]['open']) * 100
                percentage_2 = (float(arr[idx - 2]['close']) - float(arr[idx - 2]['open'])) / float(
                    arr[idx - 2]['open']) * 100
                percentage_3 = (float(arr[idx - 3]['close']) - float(arr[idx - 3]['open'])) / float(
                    arr[idx - 3]['open']) * 100
                percentage_4 = (float(arr[idx - 4]['close']) - float(arr[idx - 4]['open'])) / float(
                    arr[idx - 4]['open']) * 100
                slope = (percentage_1 + percentage_2 + percentage_3 + percentage_4) / 4
                initial_price = float(x['close'])
                timestamp = str(x['timestamp'])
                if (slope > 0 and percentage > 0 and percentage - slope > percentage_input) or (
                        slope < 0 and percentage < 0 and percentage - slope < -percentage_input):
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
        bar_percentage = 0

        arr = list(reversed(get_historical_price(symbol=symbol['symbol'], currency='BUSD', interval=interval, limit=3)))
        if len(arr) > 0:
            if float(arr[1]['open']) < float(arr[1]['close']):
                percentage_calc = (float(arr[1]['close']) - float(arr[1]['open'])) / float(arr[1]['open']) * 100
            else:
                percentage_calc = (float(arr[1]['open']) - float(arr[1]['close'])) / float(arr[1]['close']) * 100

            print("Symbol {}: Actual Price : {} Previous Price : {} Percentage {} Bar Percentage {} at {}".format(
                symbol['symbol'],
                float(arr[1]['close']),
                float(arr[1]['open']),
                percentage_calc, bar_percentage, arr[1]['timestamp']))

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


# backtest_percentage(2, 1000, '1h',False)
# backtest_percentage(percentage_input=5, limit=1000, interval='4h', print_bool=True)
# signal_crypto_percentage(2, '1h')
# backtest_percentage_slope(1, 1000, '1h')
# export_history()
read_file()

