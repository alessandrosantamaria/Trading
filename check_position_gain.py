from datetime import date, datetime

import MetaTrader5 as mt5

from constraints import *
from mt5_open_close_orders import *
from telegram_message import send_scalping_scalping, send_message_telegram_open_trade


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
                if order.identifier not in listPositionIds and order.tp != 0 and order.comment == SCALPING_STRATEGY:
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


def check_position_gain_for_scalping_strategy(listAccount):
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
            listSymbols = []
            for order in openOrders:
                if order.symbol not in listSymbols:
                    listSymbols.append(order.symbol)

            for symbol in listSymbols:
                orders_to_check = mt5.positions_get(symbol=symbol)
                for single_order in orders_to_check:
                    profit = profit + single_order.profit

                if profit > 0 and len(orders_to_check) > 1:
                    for single_order in orders_to_check:

                        order_type = single_order.type
                        symbol = single_order.symbol
                        volume = single_order.volume
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
                            "position": single_order.ticket,
                            "price": price,
                            "magic": 234000,
                            "comment": SCALPING_STRATEGY,
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }

                        mt5.order_send(close_request)
                        open_trade(action, symbol, listAccount, SHORT_STRATEGY)
                        send_profit_after_hedge(profit,symbol)


def check_hedge_for_scalp_strategy(listAccount):
    if date.today().weekday() < 5 or (
            date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            loss_pips = 0
            symbol = ''

            for order in openOrders:

                if order.comment == SCALPING_STRATEGY and order.profit < 0:
                    loss_pips = abs(order.price_open - order.price_current)
                    symbol = order.symbol
                if loss_pips > retrieve_symbol_pip(symbol):

                    if order.type == 0:
                        trade_type = mt5.ORDER_TYPE_SELL
                        price = mt5.symbol_info_tick(symbol).bid
                        action = 'SELL'

                    else:
                        trade_type = mt5.ORDER_TYPE_BUY
                        price = mt5.symbol_info_tick(symbol).ask
                        action = 'BUY'

                    buy_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": order.volume * 4,
                        "type": trade_type,
                        "price": price,
                        # "tp": tp,
                        # "sl": sl,
                        "magic": ea_magic_number,
                        "comment": SCALPING_STRATEGY,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }

                    # send a trading request

                    result = mt5.order_send(buy_request)
                    send_message_telegram_hedge(symbol, order.volume * 4, action, SCALPING_STRATEGY)

def check_position_gain_scalping(listAccount):
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


            for order in openOrders:

                if order.profit > 0 and order.comment == \
                        SCALPING_STRATEGY:

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





def retrieve_symbol_pip(symbol):
    pip = 0
    if symbol in SP500_MT5:
        pip = 5
    elif symbol in XAUUSD:
        pip = 2
    elif 'JPY' in symbol:
        pip = 0.1
    else:
        pip = 0.001

    return pip



