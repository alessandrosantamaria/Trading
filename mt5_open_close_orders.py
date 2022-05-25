from datetime import date, datetime

import MetaTrader5 as mt5

import accounts
from telegram_message import *
import math

ea_magic_number = 9986989  # if you want to give every bot a unique identifier


def get_info(symbol):
    # get symbol properties
    info = mt5.symbol_info(symbol)
    return info


def open_trade_manual_execution(action, symbol, listBroker, tp, sl, lotInput):
    for i in listBroker:

        if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
            print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get(symbol=symbol)
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']
        # if len(openOrders) > 0:
        #    close_trade(symbol, listBroker)

        if action == 'BUY':
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
            # tp, sl = no_round_tp(price, sizeRenko, action)

        else:
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            # tp, sl = no_round_tp(price, sizeRenko, action)

        if "XAU" in symbol:
            lot = round(balance / 200000, 2)
        elif "ZAR" in symbol or DAX_MT5 in symbol:
            lot = round(balance / 200000, 2)
        elif BTC_MT5 in symbol:
            lot = round(balance / 400000, 2)
        elif DOW_MR5 in symbol or NASDAQ_MT5 in symbol:
            lot = round(balance / 100000, 1)
        elif SP500_MT5 in symbol:
            lot = round(balance / 50000, 1)
        elif GOOGLE_MT5 in symbol or AMAZON_MT5 in symbol or TESLA_MT5 in symbol:
            lot = 0.1
        elif APPLE_MT5 in symbol:
            lot = 1
        elif NETFLIX_MT5 in symbol:
            lot = 0.2
        else:
            lot = round(balance / 100000, 2)

        if NASDAQ_MT5 in symbol or DOW_MR5 in symbol or SP500_MT5 in symbol or DAX_MT5 in symbol:
            lot = round(lot * lotInput, 1)
        elif "JPY" in symbol:
            lot = round(lot * lotInput, 2)
        else:
            lot = round(lot * lotInput, 2)

        if symbol == "BTCUSD" or symbol == "ETHUSD" or symbol == APPLE_MT5 or symbol == TESLA_MT5 or symbol == NETFLIX_MT5 or symbol == GOOGLE_MT5 or symbol == AMAZON_MT5:
            typeFilling = mt5.ORDER_FILLING_FOK
        else:
            typeFilling = mt5.ORDER_FILLING_IOC

        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": trade_type,
            "price": price,
            "tp": tp,
            "sl": sl,
            "magic": ea_magic_number,
            "comment": i["strategyManual"],
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": typeFilling,
        }

        # send a trading request
        send_message_telegram_open_trade(symbol, lot, action, i["strategyManual"])
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


def open_trade(action, symbol, listBroker, strategy):
    if (date.today().weekday() == 4 and symbol != BTC_MT5) or date.today().weekday() < 5 or (
            date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for i in listBroker:

            if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
                print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get(symbol=symbol)

            if len(openOrders) > 0:
              close_trade(symbol, listBroker, strategy)

            if action == 'BUY':
                trade_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
                # tp, sl = round_sl_tp(price,  symbol, action)

            else:
                trade_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
                # tp, sl = round_sl_tp(price, sizeRenko, symbol, action)

            if DAX_MT5 in symbol:
                lot = 0.1
            else:
                lot = round(lot_calculation(symbol) / 2,2)

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
                # "tp": tp,
                # "sl": sl,
                "magic": ea_magic_number,
                "comment": strategy,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": typeFilling,
            }

            # send a trading request
            send_message_telegram_open_trade(symbol, lot, action, strategy)
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


def open_trade_scalping(action, symbol, listBroker, renko):
    if (date.today().weekday() == 4 and symbol != BTC_MT5) or date.today().weekday() < 5 or (
            date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for i in listBroker:

            if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
                print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get(symbol=symbol)
            orderFound = False


            if orderFound == False:
                if action == 'BUY':
                    trade_type = mt5.ORDER_TYPE_BUY
                    price = mt5.symbol_info_tick(symbol).ask
                    tp, sl = no_round_tp(price, renko, action)

                else:
                    trade_type = mt5.ORDER_TYPE_SELL
                    price = mt5.symbol_info_tick(symbol).bid
                    tp, sl = no_round_tp(price, renko, action)

                if DAX_MT5 in symbol:
                    lot = 0.1
                elif SP500_MT5 in symbol:
                    lot = 0.5
                else:
                    lot = lot_calculation(symbol)

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
                    "tp": tp,
                    "sl": sl,
                    "magic": ea_magic_number,
                    "comment": SCALPING_STRATEGY,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": typeFilling,
                }

                # send a trading request
                send_message_telegram_open_trade(symbol, lot, action, SCALPING_STRATEGY)
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


def close_trade(symbol, listBroker, strategy):
    for i in listBroker:
        if date.today().weekday() == 4 and symbol != "BTCUSD" or date.today().weekday() < 5:
            if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
                print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get(symbol=symbol)

            if len(openOrders) > 0:
                for order in openOrders:
                    if order.comment == strategy:

                        order_type = order.type
                        symbol = order.symbol
                        volume = order.volume

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
                            "position": order.ticket,
                            "price": price,
                            "magic": 234000,
                            "comment": order.comment,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": typeFilling,
                        }

                        mt5.order_send(close_request)
                        account_info_dict = mt5.account_info()._asdict()
                        balance = account_info_dict['balance']
                        if strategy != SCALPING_STRATEGY:
                            send_message_telegram_close_trade(symbol, order.profit)
                            send_message_telegram_update_gain_balance(balance)


def round_sl_tp(price, sizeRenko, symbol, action):
    if action == "BUY":
        if "JPY" in symbol:
            tp = price + sizeRenko
            sl = price - (sizeRenko * 2)
        elif symbol == NASDAQ_MT5 or symbol == SP500_MT5 or symbol == DAX_MT5:
            tp = price + sizeRenko
            sl = price - sizeRenko * 2
        elif symbol == "XAUUSD":
            tp = price + sizeRenko
            sl = price - (sizeRenko * 2)
        elif symbol == BTC_MT5:
            tp = round(price + sizeRenko, -2)
            sl = round(price - sizeRenko * 2, -2)
        else:
            tp = price + sizeRenko
            sl = price - (sizeRenko * 2)
    else:
        if "JPY" in symbol:
            tp = price - sizeRenko
            sl = price + (sizeRenko * 2)
        elif symbol == NASDAQ_MT5 or symbol == SP500_MT5 or symbol == DAX_MT5:
            tp = round(price - sizeRenko)
            sl = round(price + sizeRenko * 2)
        elif symbol == BTC_MT5:
            tp = round(price - sizeRenko, -2)
            sl = round(price + sizeRenko * 2, -2)
        elif symbol == "XAUUSD":
            tp = price - sizeRenko
            sl = price + (sizeRenko * 2)
        else:
            tp = price - sizeRenko
            sl = price + (sizeRenko * 2)
    return tp, sl




def round_tp(price, sizeRenko, symbol, action):
    if action == "BUY":
        if "JPY" in symbol:
            tp = round(price + sizeRenko, 1)
            sl = round(price - sizeRenko * 2, 1)
        elif symbol == NASDAQ_MT5 or symbol == SP500_MT5 or symbol == DAX_MT5:
            tp = round(price + sizeRenko, -1)
            sl = round(price - sizeRenko * 2, -1)
        elif symbol == "XAUUSD":
            tp = round(price + sizeRenko)
            sl = round(price - sizeRenko * 2)
        elif symbol == BTC_MT5:
            tp = round(price + sizeRenko, -2)
            sl = round(price - sizeRenko * 2, -2)
        else:
            tp = round(price + sizeRenko, 3)
            sl = round(price - sizeRenko * 2, 3)
    else:
        if "JPY" in symbol:
            tp = round(price - sizeRenko, 1)
            sl = round(price + sizeRenko * 2, 1)
        elif symbol == NASDAQ_MT5 or symbol == SP500_MT5 or symbol == DAX_MT5:
            tp = round(price - sizeRenko, -1)
            sl = round(price + sizeRenko * 2, -1)
        elif symbol == BTC_MT5:
            tp = round(price - sizeRenko, -2)
            sl = round(price + sizeRenko * 2, -2)
        elif symbol == "XAUUSD":
            tp = float(round(price - sizeRenko))
            sl = round(price + sizeRenko * 2)
        else:
            tp = round(price - sizeRenko, 3)
            sl = round(price + sizeRenko * 2, 3)

    return tp, sl


def no_round_tp(price, sizeRenko, action):
    if action == "BUY":
        tp = price + sizeRenko
        sl = price - sizeRenko

    else:
        tp = price - sizeRenko
        sl = price + sizeRenko

    return tp, sl


def lot_calculation(symbol):
    account_info_dict = mt5.account_info()._asdict()
    balance = account_info_dict['balance']
    if "XAU" in symbol:
        lot = round(balance / 200000, 2)
    elif "ZAR" in symbol or DAX_MT5 in symbol:
        lot = round(balance / 200000, 2)
    elif BTC_MT5 in symbol:
        lot = round(balance / 200000, 2)
    elif DOW_MR5 in symbol or NASDAQ_MT5 in symbol:
        lot = round(balance / 50000, 1)
    elif SP500_MT5 in symbol:
        lot = round(balance / 50000, 1)
    else:
        lot = round(balance / 100000, 2)

    if NASDAQ_MT5 in symbol or DOW_MR5 in symbol or SP500_MT5 in symbol or DAX_MT5 in symbol:
        lot = round(lot * accounts.broker["lot"], 2)
    else:
        lot = round(lot * accounts.broker["lot"], 2)

    return lot


