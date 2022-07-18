import time

from twelvedata import TDClient

# Initialize client - apikey parameter is requiered
from accounts import listBroker
from constraints import *
from mt5_open_close_orders import open_trade_manual_execution
from telegram_message import send_message_api


def check_trade(symbol, pips, interval_timeframe, target):
    symbol_dict = symbols[symbol]

    td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")

    # Construct the necessary time series
    ts = td.time_series(
        symbol=symbol_dict["api"],
        interval=interval_timeframe,
        outputsize=5000,
        timezone="Europe/Rome",

    ).with_rsi().with_ema(time_period=200)

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

    print("Symbol {}\nSuccess : {}\nFailed : {}".format(symbol, count_success, count_failed))


def open_trade_api(symbol= 'symbol', target = 'target',bar_pips= 'bar_pips',time_interval= 'time_interval',lot = 'lot',send_message = 'send_message'):
    symbol_dict = symbols[symbol]

    td = TDClient(apikey="39e4ae9c3f554c1696fec4c21cdd7dc4")

    # Construct the necessary time series
    ts = td.time_series(
        symbol=symbol_dict["api"],
        interval=time_interval,
        outputsize=2,
        timezone="Europe/Rome",

    )

    json = ts.as_json()
    bar_percentage = 0
    if "XAU" in symbol:
        pips = int(bar_pips / 3)
        value_to_compare = abs(int(float(json[1]['open'])) - float(json[1]['close']))
    else:
        pips = bar_pips
        value_to_compare = int(abs(float(json[1]['open']) - float(json[1]['close'])) * 10000)
    if int(abs(float(json[1]['open']) - float(json[1]['close'])) * 10000) > 1:
        bar_percentage = ((int(abs(float(json[1]['open']) - float(json[1]['close'])) * 10000)) / (
            int(abs(float(json[1]['low']) - float(json[1]['high'])) * 10000))) * 100
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
             open_trade_manual_execution(action, symbol_dict["mt4"], listBroker, sizeRenko * (target / 10), lot)


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
single_pip = 5
single_target = 5
#print('Check trades for interval {} and pips bar {} having target {}'.format(single_time, single_pip, single_target))

#for value in [AUDUSD, EURUSD, GBPUSD, NZDUSD, USDCAD, USDCHF]:
#for key, value in symbols.items():
#    check_trade(AUDUSD, single_pip, single_time, single_target)
#    time.sleep(10)
