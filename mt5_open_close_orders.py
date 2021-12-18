import sys
from datetime import date

import MetaTrader5 as mt5

from constraints import *
from telegram import *

ea_magic_number = 9986989  # if you want to give every bot a unique identifier


def get_info(symbol):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5symbolinfo_py
    '''
    # get symbol properties
    info = mt5.symbol_info(symbol)
    return info


def open_trade(action, symbol, listBroker):
    if (date.today().weekday() == 4 and symbol != 'BTCUSD') or date.today().weekday() < 5:
        for i in listBroker:

            if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
                print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get(symbol=symbol)
            account_info_dict = mt5.account_info()._asdict()
            balance = account_info_dict['balance']
            if len(openOrders) > 0:
                close_trade(symbol, listBroker)

            if action == 'BUY':
                trade_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask



            elif action == 'SELL':
                trade_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid

            if "XAU" in symbol:
                lot = round(balance / 200000, 2)
            elif "ZAR" in symbol:
                lot = round(balance / 200000, 2)
            elif BTC_MT5 in symbol:
                lot = round(balance / 400000, 2)
            elif NASDAQ_MT5 in symbol:
                lot = round(balance / 50000, 1)
            elif DAX_MT5 in symbol:
                lot = round(balance / 50000, 1)
            elif SP500_MT5 in symbol:
                lot = round(balance / 100000, 1)
            else:
                lot = round(balance / 100000, 2)

            lot = lot * i["lot"]

            if symbol == "BTCUSD" or symbol == "ETHUSD":
                typeFilling = mt5.ORDER_FILLING_FOK
            else:
                typeFilling = mt5.ORDER_FILLING_IOC

            buy_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": trade_type,
                "price": price,
                "magic": ea_magic_number,
                "comment": "Scalping",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": typeFilling,
            }

            # send a trading request
            send_message_telegram_open_trade(symbol, lot)
            result = mt5.order_send(buy_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print("[x] order_send failed, retcode={}".format(result.retcode))
                # request the result as a dictionary and display it element by element
                result_dict = result._asdict()
                for field in result_dict.keys():
                    print("{}={}".format(field, result_dict[field]))
                    # if this is a trading request structure, display it element by element as well
                    if field == "request":
                        traderequest_dict = result_dict[field]._asdict()
                        for tradereq_filed in traderequest_dict:
                            print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

            else:

                print("Order successfully placed in broker account {}!".format(i["login"]))


def close_trade(symbol, listBroker):
    for i in listBroker:
        if date.today().weekday() == 4 and symbol != "BTCUSD":
            if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
                print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get(symbol=symbol)

            if len(openOrders) > 0:

                order_type = openOrders[0].type
                symbol = openOrders[0].symbol
                volume = openOrders[0].volume

                if order_type == mt5.ORDER_TYPE_BUY:
                    order_type = mt5.ORDER_TYPE_SELL
                    price = mt5.symbol_info_tick(symbol).bid
                else:
                    order_type = mt5.ORDER_TYPE_BUY
                    price = mt5.symbol_info_tick(symbol).ask

                if symbol == BTC_MT5:
                    typeFilling = mt5.ORDER_FILLING_FOK
                else:
                    typeFilling = mt5.ORDER_FILLING_IOC

                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": float(volume),
                    "type": order_type,
                    "position": openOrders[0].ticket,
                    "price": price,
                    "magic": 234000,
                    "comment": "Close trade",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": typeFilling,
                }
                send_message_telegram_close_trade(symbol, openOrders[0].profit)
                mt5.order_send(close_request)
                account_info_dict = mt5.account_info()._asdict()
                balance = account_info_dict['balance']
                send_message_telegram_update_gain_balance(balance)


def open_trade_martingale(action, symbol, listBroker):
    for i in listBroker:

        if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
            print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get(symbol=symbol)
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']
        if len(openOrders) > 0:
            close_trade(symbol, listBroker)

        if action == 'BUY':
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask



        elif action == 'SELL':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid

        if "XAU" in symbol:
            lot = round(balance / 200000, 2)
        elif "ZAR" in symbol:
            lot = round(balance / 200000, 2)
        elif BTC_MT5 in symbol:
            lot = round(balance / 400000, 2)
        elif NASDAQ_MT5 in symbol:
            lot = round(balance / 50000, 1)
        elif DAX_MT5 in symbol:
            lot = round(balance / 50000, 1)
        elif SP500_MT5 in symbol:
            lot = round(balance / 100000, 1)
        else:
            lot = round(balance / 100000, 2)

        lot = lot * i["lot"]
        if symbols[symbol] > 0:
            lot = lot * symbols[symbol]

        if symbol == "BTCUSD" or symbol == "ETHUSD":
            typeFilling = mt5.ORDER_FILLING_FOK
        else:
            typeFilling = mt5.ORDER_FILLING_IOC

        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": trade_type,
            "price": price,
            "magic": ea_magic_number,
            "comment": "Scalping",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": typeFilling,
        }

        # send a trading request
        result = mt5.order_send(buy_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("[x] order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("{}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

        else:

            print("Order successfully placed in broker account {}!".format(i["login"]))


def close_trade_martingale(symbol, listBroker):
    for i in listBroker:

        if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
            print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get(symbol=symbol)
        if len(openOrders) > 0:

            order_type = openOrders[0].type
            symbol = openOrders[0].symbol
            volume = openOrders[0].volume

            if order_type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask

            if symbol == BTC_MT5:
                typeFilling = mt5.ORDER_FILLING_FOK
            else:
                typeFilling = mt5.ORDER_FILLING_IOC

            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "position": openOrders[0].ticket,
                "price": price,
                "magic": 234000,
                "comment": "Close trade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": typeFilling,
            }
            if openOrders[0].profit < 0:
                symbols[symbol] = symbols[symbol] + 1
            else:
                symbols[symbol] = 0

            mt5.order_send(close_request)
