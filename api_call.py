import datetime
import json as js
import time

from twelvedata import TDClient

# Initialize client - apikey parameter is requiered
from accounts import listBroker
from constraints import *
from mt5_open_close_orders import open_trade_manual_execution
from telegram_message import send_message_api


def write_history_file(interval_timeframe):
    hist = {}
    for key, value in symbols.items():
        td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")

        # Construct the necessary time series
        ts = td.time_series(
            symbol=value["api"],
            interval=interval_timeframe,
            outputsize=5000,
            timezone="UTC",

        ).with_percent_b().with_ema(time_period=50)
        json_export = tuple(reversed(ts.as_json()))
        dict = {
            '{}'.format(value['mt4']): list(json_export)
        }
        hist.update(dict)
        time.sleep(10)

    with open('history.txt', 'w') as file:
        file.write(js.dumps(hist))


def check_trade_from_file(symbol, pips, interval_timeframe, target):
    # symbol_dict = symbols[symbol]
    #
    # td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")
    #
    ## Construct the necessary time series
    # ts = td.time_series(
    #    symbol=symbol_dict["api"],
    #    interval=interval_timeframe,
    #    outputsize=5000,
    #    timezone="UTC",
    #
    # )
    #
    # json = tuple(reversed(ts.as_json()))
    with open('history.txt') as f:
        data = f.read()

        json = js.loads(data)

    for key, value in json.items():
        count_success = 0
        count_failed = 0
        conversion = 0

        if "XAU" in key:
            pips = int(pips / 3)
        else:
            pips = pips
        for idx, x in enumerate(value):
            if int(abs(float(x['open']) - float(x['close'])) * 10000) > 1:
                bar_percentage = ((int(abs(float(x['open']) - float(x['close'])) * 10000)) / (
                    int(abs(float(x['low']) - float(x['high'])) * 10000))) * 100
            else:
                bar_percentage = 1

            if "XAU" in key:
                value_to_compare = abs(int(float(x['open'])) - float(x['close']))
                conversion = 1
            elif "JPY" in key:
                value_to_compare = int(abs(float(x['open']) - float(x['close'])) * 100)
                conversion = 100
            else:
                value_to_compare = int(abs(float(x['open']) - float(x['close'])) * 10000)
                conversion = 10000
            if idx + 1 != len(value):
                sub_array = value[idx + 1: len(value)]
                # print('Symbol {} - Date {}'.format(symbol,x['datetime']))

                if value_to_compare > pips and x != sub_array[-1] and bar_percentage > 80:
                    # print("Trade found at {} for symbol {}".format(x['datetime'], symbol))
                    for sub_element in sub_array:
                        duplicate_count = count_success
                        if float(x['open']) > float(x['close']):
                            if int((float(x['close']) - float(sub_element['close'])) * conversion) > target:
                                count_success += 1

                                #    print("Trade end with success with open timestamp {} and close timestamp {} for symbol {} due to open price is {} and close price is {} with operation {}".format(
                                #          x['datetime'], sub_element['datetime'], symbol, x['close'], sub_element['close'],
                                #          'SELL'))
                                break

                        else:
                            if int((float(sub_element['close']) - float(x['close'])) * conversion) > target:
                                count_success += 1
                                # print(
                                #         "Trade end with success with open timestamp {} and close timestamp {} for symbol {} due to open price is {} and close price is {} with operation {}".format(
                                #                x['datetime'], sub_element['datetime'], symbol, x['close'], sub_element['close'],
                                #                'BUY'))
                                break

                    if count_success == duplicate_count:
                        count_failed += 1
                        # print("Trade end with failed at {} for symbol {} due to open price is {} ".format(x['datetime'], symbol, x['close']))

        print("Symbol {}\nSuccess : {}\nFailed : {}".format(key, count_success, count_failed))


def check_trade_from_api(symbol, pips, interval_timeframe, target):
    symbol_dict = symbols[symbol]
    td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")
    # Construct the necessary time series
    ts = td.time_series(
        symbol=symbol_dict["api"],
        interval=interval_timeframe,
        outputsize=5000,
        timezone="UTC",
    ).with_percent_b().with_ema(time_period=50)

    json = tuple(reversed(ts.as_json()))

    count_success = 0
    count_failed = 0
    conversion = 0

    if "XAU" in symbol:
        pips = int(pips / 3)
    else:
        pips = pips
    for idx, x in enumerate(json):
        if int(abs(float(x['open']) - float(x['close'])) * 10000) > 1:
            bar_percentage = ((int(abs(float(x['open']) - float(x['close'])) * 10000)) / (
                int(abs(float(x['low']) - float(x['high'])) * 10000))) * 100
        else:
            bar_percentage = 1

        if "XAU" in symbol:
            value_to_compare = abs(int(float(x['open'])) - float(x['close']))
            conversion = 1
        elif "JPY" in symbol:
            value_to_compare = int(abs(float(x['open']) - float(x['close'])) * 100)
            conversion = 100
        else:
            value_to_compare = int(abs(float(x['open']) - float(x['close'])) * 10000)
            conversion = 10000
        if idx + 1 != len(json):
            sub_array = json[idx + 1: len(json)]
            # print('Symbol {} - Date {}'.format(symbol,x['datetime']))

            if value_to_compare > pips and x != sub_array[-1] and bar_percentage > 80:
                # print("Trade found at {} for symbol {}".format(x['datetime'], symbol))
                for sub_element in sub_array:
                    duplicate_count = count_success
                    if float(x['open']) > float(x['close']):
                        if int((float(x['close']) - float(sub_element['close'])) * conversion) > target:
                            count_success += 1

                            print(
                                "Trade end with success with open timestamp {} and close timestamp {} for symbol {} due to open price is {} and close price is {} with operation {} with percent b {}".format(
                                    x['datetime'], sub_element['datetime'], symbol, x['close'],
                                    sub_element['close'],
                                    'SELL', x['percent_b']))
                            break

                    else:
                        if int((float(sub_element['close']) - float(x['close'])) * conversion) > target:
                            count_success += 1
                            print(
                                "Trade end with success with open timestamp {} and close timestamp {} for symbol {} due to open price is {} and close price is {} with operation {} with percent b {}".format(
                                    x['datetime'], sub_element['datetime'], symbol, x['close'],
                                    sub_element['close'],
                                    'BUY', x['percent_b']))
                            break

                if count_success == duplicate_count:
                    count_failed += 1
                    print("Trade end with failed at {} for symbol {} due to open price is {} with percent b {}".format(x['datetime'], symbol, x['close'],x['percent_b']))

    print("Symbol {}\nSuccess : {}\nFailed : {}".format(symbol, count_success, count_failed))




def check_trade_percentage(symbol, percentage_input, interval_timeframe, target):
    symbol_dict = symbols[symbol]

    td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")

    # Construct the necessary time series
    ts = td.time_series(
        symbol=symbol_dict["api"],
        interval=interval_timeframe,
        outputsize=5000,
        timezone="UTC",

    )

    json = tuple(reversed(ts.as_json()))
    count_success = 0
    count_failed = 0
    conversion = 0

    for idx, x in enumerate(json):
        if "XAU" in symbol:
            value_to_compare = abs(int(float(x['open'])) - float(x['close']))
            conversion = 1
        elif "JPY" in symbol:
            value_to_compare = int(abs(float(x['open']) - float(x['close'])) * 100)
            conversion = 100
        else:
            value_to_compare = int(abs(float(x['open']) - float(x['close'])) * 10000)
            conversion = 10000
        if idx != 0:
            if float(x['close']) > float(x['open']):
                  percentage = (float(x['close']) - float(x['open'])) / float(x['open']) * 100
            else:
                  percentage = ((float(x['close']) - float(x['open'])) / float(x['open']) * 100)
            initial_price = float(x['close'])
            timestamp = str(x['datetime'])
            if percentage > percentage_input or percentage <  -percentage_input:
                sub_array = json[idx + 1: len(json)]
                if percentage > percentage_input:
                    action = 'BUY'
                else:
                    action = 'SELL'
                for sub in sub_array:
                    if action == 'BUY':
                        pips = (float(sub['high'])-initial_price) * conversion
                        final_price = sub['high']
                    else:
                        pips = (float(sub['low'])-initial_price) * conversion
                        final_price = sub['low']
                    if (pips > target and action == 'BUY') or (pips < -target and action == 'SELL'):
                        count_success += 1
                        found = True
                        print(
                            'Order opened {} with price {} for symbol {} close at {} at price {} with percentage earned {}'.format(
                                timestamp, initial_price, symbol, str(sub['datetime']), final_price, target))

                        break
                if found == False:
                    count_failed += 1
                    print(
                        'Order opened {} with price {} for symbol {} is a loss trade'.format(timestamp,
                                                                                             initial_price,
                                                                                             symbol))

    print('Win Trades {} - Lose Trades {}'.format(count_success, count_failed))


def check_trade_percentage_slope(symbols, percentage_input, interval_timeframe, target):
    # td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")
    #
    ## Construct the necessary time series
    # ts = td.time_series(
    #    symbol=symbol_dict["api"],
    #    interval=interval_timeframe,
    #    outputsize=5000,
    #    timezone="UTC",)

    # json = tuple(reversed(ts.as_json()))

    with open('history.txt') as f:
        data = f.read()

        json = js.loads(data)

    for key, value in json.items():
        count_success = 0
        count_failed = 0
        found = False

        for idx, x in enumerate(value):
            if "XAU" in key:
                conversion = 1
            elif "JPY" in key:
                conversion = 100
            else:
                conversion = 10000
            if idx > 4:
                percentage = (float(x['close']) - float(x['open'])) / float(x['open']) * 100
                percentage_1 = (float(value[idx - 1]['close']) - float(value[idx - 1]['open'])) / float(
                    value[idx - 1]['open']) * 100
                percentage_2 = (float(value[idx - 2]['close']) - float(value[idx - 2]['open'])) / float(
                    value[idx - 2]['open']) * 100
                percentage_3 = (float(value[idx - 3]['close']) - float(value[idx - 3]['open'])) / float(
                    value[idx - 3]['open']) * 100
                percentage_4 = (float(value[idx - 4]['close']) - float(value[idx - 4]['open'])) / float(
                    value[idx - 4]['open']) * 100
                slope = (percentage_1 + percentage_2 + percentage_3 + percentage_4) / 4
                initial_price = float(x['close'])
                timestamp = str(x['datetime'])
                pip_bar = abs((float(x['close']) - float(x['open'])) * conversion)
                pip_bar_1 = abs((float(value[idx - 1]['close']) - float(value[idx - 1]['open'])) * conversion)
                pip_bar_2 = abs((float(value[idx - 2]['close']) - float(value[idx - 2]['open'])) * conversion)
                pip_bar_3 = abs((float(value[idx - 3]['close']) - float(value[idx - 3]['open'])) * conversion)
                pip_bar_4 = abs((float(value[idx - 4]['close']) - float(value[idx - 4]['open'])) * conversion)

                if (pip_bar > pip_bar_1 and pip_bar > pip_bar_2 and pip_bar > pip_bar_3 and pip_bar > pip_bar_4) and (
                        (slope > 0 and percentage > 0 and percentage - slope > percentage_input) or (
                        slope < 0 and percentage < 0 and percentage - slope < -percentage_input)):
                    sub_array = value[idx + 1: len(value)]
                    if percentage > 0:
                        action = 'BUY'
                    else:
                        action = 'SELL'
                    for sub in sub_array:
                        duplicate_count = count_success
                        pips = (float(sub['close']) - float(sub['open'])) * conversion
                        if (initial_price < float(sub['high']) and pips > target and action == 'BUY') or (
                                initial_price > float(sub['low']) and pips < -target and action == 'SELL'):
                            count_success += 1
                            found = True
                            if action == 'BUY':
                                price_close_operation = sub['high']
                            else:
                                price_close_operation = sub['low']
                            print(
                                'Order {} opened {} with price {} for symbol {} close at {} at price {} with percentage earned {}'.format(
                                    action,
                                    timestamp, initial_price, key, str(sub['datetime']), price_close_operation, target))
                            break
                    if count_success == duplicate_count:
                        count_failed += 1
                        print(
                            'Order opened {} with price {} for symbol {} is a loss trade'.format(timestamp,
                                                                                                 initial_price,
                                                                                                 key))

        print('Win Trades {} - Lose Trades {}'.format(count_success, count_failed))


def open_trade_api(symbol='symbol', target='target', bar_pips='bar_pips', time_interval='time_interval', lot='lot',
                   send_message='send_message'):
    symbol_dict = symbols[symbol]

    td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")

    # Construct the necessary time series
    ts = td.time_series(
        symbol=symbol_dict["api"],
        interval=time_interval,
        outputsize=3,
        timezone="UTC",

    )

    json = ts.as_json()
    json_time = datetime.datetime.strptime(json[0]['datetime'], '%Y-%m-%d %H:%M:%S')
    current_time = datetime.datetime.now()
    print('current time {} - json time {}'.format(current_time,json_time))

    if (json_time-current_time).total_seconds()>-600:
        json = json[1:]

    bar_percentage = 0
    if "XAU" in symbol:
        conversion = 1
    elif "JPY" in symbol:
        conversion = 100
    else:
        conversion = 10000

    if "XAU" in symbol:
        pips = int(bar_pips / 3)
        value_to_compare = abs(int(float(json[1]['open'])) - float(json[1]['close']))
    else:
        pips = bar_pips
        value_to_compare = int(abs(float(json[1]['open']) - float(json[1]['close'])) * conversion)
    if int(abs(float(json[1]['open']) - float(json[1]['close'])) * conversion) > 1:
        bar_percentage = ((int(abs(float(json[1]['open']) - float(json[1]['close'])) * conversion)) / (
            int(abs(float(json[1]['low']) - float(json[1]['high'])) * conversion))) * 100
    else:
        bar_percentage = 1

    if value_to_compare > pips and bar_percentage > 75:

        if float(json[1]['open']) > float(json[1]['close']):

            action = 'SELL'
        else:

            action = 'BUY'
        if "JPY" in symbol_dict["mt4"]:
            sizeRenko = 0.1
        elif "ZAR" in symbol_dict["mt4"]:
            sizeRenko = 0.03
        elif "XAUUSD" in symbol_dict["mt4"]:
            sizeRenko = 2
        elif "BTC" in symbol_dict["mt4"]:
            sizeRenko = 500
        elif "500" in symbol_dict["mt4"]:
            sizeRenko = 5
        elif "100" in symbol_dict["mt4"]:
            sizeRenko = 25
        elif "30" in symbol_dict["mt4"]:
            sizeRenko = 40
        elif "GER" in symbol_dict["mt4"]:
            sizeRenko = 30
        else:
            sizeRenko = 0.001




        if send_message == True:
            send_message_api(symbol)
        else:
            print('Using the candle of {}'.format(datetime.datetime.strptime(json[0]['datetime'], '%Y-%m-%d %H:%M:%S')))
            open_trade_manual_execution(action, symbol_dict["mt4"], listBroker, sizeRenko * (target / 10), lot)


def open_trade_api_percentage_slope(symbol='symbol', target='target', percentage_input='percentage_input',
                                    time_interval='time_interval', lot='lot', send_message='send_message'):
    symbol_dict = symbols[symbol]

    td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")

    # Construct the necessary time series
    ts = td.time_series(
        symbol=symbol_dict["api"],
        interval=time_interval,
        outputsize=7,
        timezone="UTC"

    )

    json = ts.as_json()
    json_time = datetime.datetime.strptime(json[0]['datetime'], '%Y-%m-%d %H:%M:%S')
    current_time = datetime.datetime.now()
    if "XAU" in symbol:
        conversion = 1
    elif "JPY" in symbol:
        conversion = 100
    else:
        conversion = 10000
    if current_time.minute > 30:
        current_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    elif current_time.minute > 0:
        current_time = datetime.datetime.now().replace(minute=30, second=0, microsecond=0)

    if json_time != current_time:
        json = json[1:]

    percentage = (float(json[0]['close']) - float(json[0]['open'])) / float(json[0]['open']) * 100
    percentage_1 = (float(json[1]['close']) - float(json[1]['open'])) / float(
        json[1]['open']) * 100
    percentage_2 = (float(json[2]['close']) - float(json[2]['open'])) / float(
        json[2]['open']) * 100
    percentage_3 = (float(json[3]['close']) - float(json[3]['open'])) / float(
        json[3]['open']) * 100
    percentage_4 = (float(json[4]['close']) - float(json[4]['open'])) / float(
        json[4]['open']) * 100
    slope = (percentage_1 + percentage_2 + percentage_3 + percentage_4) / 4
    pip_bar = abs((float(json[0]['close']) - float(json[0]['open'])) * conversion)
    pip_bar_1 = abs((float(json[1]['close']) - float(json[1]['open'])) * conversion)
    pip_bar_2 = abs((float(json[2]['close']) - float(json[2]['open'])) * conversion)
    pip_bar_3 = abs((float(json[3]['close']) - float(json[3]['open'])) * conversion)
    pip_bar_4 = abs((float(json[4]['close']) - float(json[4]['open'])) * conversion)

    if (pip_bar > pip_bar_1 and pip_bar > pip_bar_2 and pip_bar > pip_bar_3 and pip_bar > pip_bar_4) and (
            slope > 0 and percentage > 0 and percentage - slope > percentage_input) or (
            slope < 0 and percentage < 0 and percentage - slope < -percentage_input):
        if percentage > 0:
            action = 'BUY'
        else:
            action = 'SELL'

        if "JPY" in symbol_dict["mt4"]:
            sizeRenko = 0.1
        elif "ZAR" in symbol_dict["mt4"]:
            sizeRenko = 0.03
        elif "XAUUSD" in symbol_dict["mt4"]:
            sizeRenko = 2
        elif "BTC" in symbol_dict["mt4"]:
            sizeRenko = 500
        elif "500" in symbol_dict["mt4"]:
            sizeRenko = 5
        elif "100" in symbol_dict["mt4"]:
            sizeRenko = 25
        elif "30" in symbol_dict["mt4"]:
            sizeRenko = 40
        elif "GER" in symbol_dict["mt4"]:
            sizeRenko = 30
        else:
            sizeRenko = 0.001

        if send_message == True:
            send_message_api(symbol)
        else:
            open_trade_manual_execution(action, symbol_dict["mt4"], listBroker,
                                        sizeRenko * (target / 10), lot)


# timeframe = ['30min','1h']
# pips_bar = [5,10,15,20]
# target = [5,10,15,20]
# for single_time in timeframe:
#    for single_pip in pips_bar:
#        for single_target in target:
#            print('Check trades for interval {} and pips bar {} having target {}'.format(single_time,single_pip,single_target))
#            for key, value in symbols.items():
#              check_trade(value['mt4'],single_pip,single_time,single_target)
#              time.sleep(10)
single_time = "30min"
single_pip = 0.1
single_target = 5
# print('Check trades for interval {} and pips bar {} having target {}'.format(single_time, single_pip, single_target))

# open_trade_api_percentage_slope(symbol=EURCAD, target=5, percentage_input=0.1, time_interval="30min", lot=1, send_message=False)
# for value in [AUDUSD, EURUSD, GBPUSD, NZDUSD, USDCAD, USDCHF]:

# check_trade_percentage_slope(symbols, single_pip, single_time, single_target)
# write_history_file(single_time)

# with open('file.txt') as f:
#    data = f.read()
#
# print("Data type before reconstruction : ", type(data))
#
## reconstructing the data as a dictionary
# js = json.loads(data)
# print()

#check_trade_from_api(EURUSD, 20, single_time, single_target)
#open_trade_api(symbol=EURUSD, target=5, bar_pips=20, time_interval="30min", lot=1, send_message=False)
#for key, value in symbols.items():
#   check_trade_percentage(value['mt4'], 0.5, "4h", 20)
#   time.sleep(10)

