from datetime import date, datetime

import MetaTrader5 as mt5

from constraints import *
from mt5_open_close_orders import *
from telegram_message import send_manual_profit, send_scalping_scalping, send_message_telegram_open_trade


def retrieve_position_ids(listAccount, listPositionIds):
    if date.today().weekday() < 5 or (date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

        openOrders = mt5.positions_get()
        if len(openOrders) > 0:
            for order in openOrders:
                if order.identifier not in listPositionIds and order.tp != 0 and order.comment == MANUAL_STRATEGY:
                    listPositionIds.append(order.identifier)
        return listPositionIds


def check_position_Ids_close_orders(listAccount, listPositionIds, listCloseOrders):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                  mt5.last_error())
            quit()
        if date.today().weekday() < 5 or (
                date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
            for position in listPositionIds:
                close_order = mt5.history_deals_get(position=position)
                if len(close_order) > 0:
                    for order in close_order:
                        dict = {'time': order.time, 'symbol': order.symbol, 'profit': order.profit,
                                'order': close_order[0].order}
                        if dict['profit'] != 0.0:
                            listCloseOrders.append(dict)
                            listPositionIds.remove(position)
                            if dict['profit'] > 0:
                                print(
                                    " * Closing order {} in broker account {} with take profit {} :))!".format(
                                        dict['symbol'], singleAccount["login"], dict['profit']))
                            else:
                                print(
                                    " * Closing order {} in broker account {} with stop loss {} :((!".format(
                                        dict['symbol'], singleAccount["login"], dict['profit']))
        return listCloseOrders, listPositionIds


def check_position_gain_for_momentum_strategy(listAccount):
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

            targetProfit = (balance * singleAccount["lot"] / 50)
            for order in openOrders:

                if order.comment == SHORT_STRATEGY:
                    profit = profit + order.profit

            if profit >= targetProfit:
                for order in openOrders:
                    if order.comment == SHORT_STRATEGY:
                        order_type = order.type
                        symbol = order.symbol
                        volume = order.volume
                        action = ''

                        if order_type == mt5.ORDER_TYPE_BUY:
                            order_type = mt5.ORDER_TYPE_SELL
                            price = mt5.symbol_info_tick(symbol).bid
                            action = 'BUY'

                        else:
                            order_type = mt5.ORDER_TYPE_BUY
                            price = mt5.symbol_info_tick(symbol).ask
                            action = 'SELL'
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": float(volume),
                            "type": order_type,
                            "position": order.ticket,
                            "price": price,
                            "magic": 234000,
                            "comment": SHORT_STRATEGY,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }

                        mt5.order_send(close_request)

                send_manual_profit(profit)


def check_position_gain_for_scalp_strategy(listAccount):
    if date.today().weekday() < 5 or (
            date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            profit = 0
            account_info_dict = mt5.account_info()._asdict()
            balance = account_info_dict['balance']
            targetProfit = (balance * singleAccount["lot"] / 300)
            for order in openOrders:

                if order.comment == SCALPING_STRATEGY:
                    profit = profit + order.profit

            if profit >= targetProfit:
                for order in openOrders:
                    if order.comment == SCALPING_STRATEGY:
                        order_type = order.type
                        symbol = order.symbol
                        volume = order.volume
                        action = ''

                        if order_type == mt5.ORDER_TYPE_BUY:
                            order_type = mt5.ORDER_TYPE_SELL
                            price = mt5.symbol_info_tick(symbol).bid
                            action = 'BUY'

                        else:
                            order_type = mt5.ORDER_TYPE_BUY
                            price = mt5.symbol_info_tick(symbol).ask
                            action = 'SELL'

                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": float(volume),
                            "type": order_type,
                            "position": order.ticket,
                            "price": price,
                            "magic": 234000,
                            "comment": SCALPING_STRATEGY,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_FOK,
                        }

                        mt5.order_send(close_request)
                        if order.profit > 0:
                            open_trade(action, symbol, listAccount, SCALPING_STRATEGY)

                    send_scalping_scalping(profit)
