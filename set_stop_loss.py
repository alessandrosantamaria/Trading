from datetime import datetime, date

import MetaTrader5 as mt5
import requests

import close_all_positions
from accounts import listBroker
from constraints import *
from telegram_message import send_message_telegram_set_stop_loss


def update_position_stop_loss_for_follow_strategy(listAccount):
    if date.today().weekday() < 5 or (
            date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            account_info_dict = mt5.account_info()._asdict()
            balance = account_info_dict['balance']
            price = 0

            for order in openOrders:
                lot_size = 50

                if (order.profit > float(
                        str((balance * singleAccount["lot"] * 0.5 / lot_size))[:4]) and "{0} {1}".format(LONG_STRATEGY,"in" == order.comment)) or (order.profit > float(
                        str((balance * singleAccount["lot"] * 0.5 / (lot_size*2)))[:4]) and "{0} {1}".format(LONG_STRATEGY,"out" == order.comment)):
                    if order.type == 0:
                        price = order.price_open + abs(round(order.price_current - order.price_open, 5) / 2)

                    else:
                        price = order.price_open - abs(round(order.price_current - order.price_open, 5) / 2)

                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": order.symbol,
                        "volume": order.volume,
                        "type": order.type,
                        "position": order.ticket,
                        "price_open": order.price_open,
                        "sl": price,
                        "comment": order.comment,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }

                    if order.type == 1:
                        if order.sl == 0 or price < order.sl:
                            mt5.order_send(request)
                    elif order.type == 0:
                        if order.sl == 0 or price > order.sl:
                            mt5.order_send(request)


def update_position_stop_loss_to_price_open(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get()
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']

        request = {}

        for order in openOrders:

            if order.profit > float(
                    str((balance * singleAccount["lot"] * 0.075 / 100))[:4]) and order.sl == 0:

                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": order.type,
                    "position": order.ticket,
                    "price_open": order.price_open,
                    "sl": order.price_open,
                    "comment": "sent by python",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(request)
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
                    print(
                        "Stop Loss successfully placed to Initial Price for Pair {} with value {} in broker account {} for free ride :D!".format(
                            order.symbol, order.price_open, singleAccount["login"], round(order.profit / 2, 2)))


def set_stop_loss_manual_execution(symbol, listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get(symbol=symbol)

        for order in openOrders:
            if order.comment == singleAccount['strategyManual']:
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": order.type,
                    "position": order.ticket,
                    "price_open": order.price_open,
                    "tp": order.tp,
                    "sl": order.price_open,
                    "comment": order.comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(request)
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
                    print("Stop Loss placed at value {}".format(order.price_open))


def close_orders_after_target_for_follow_strategy(listAccount):
    if date.today().weekday() < 5 or (
            date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            account_info_dict = mt5.account_info()._asdict()
            balance = account_info_dict['balance']
            profit = 0
            for order in openOrders:
                if order.comment == LONG_STRATEGY:
                    profit = profit + order.profit

            if profit > (balance * singleAccount["lot"]) / 20:
                close_all_positions.close_all_trade_with_profit(singleAccount)
                message = '** Close All Follow Trades **\nProfit: {}$\n{}'.format(profit, '\N{money-mouth face}')
                requests.post(
                    'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM,
                                                                                           CHAT_ID_TELEGRAM,
                                                                                           message))


#update_position_stop_loss_for_follow_strategy(listBroker)