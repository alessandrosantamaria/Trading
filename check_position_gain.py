from datetime import date, datetime

import MetaTrader5 as mt5

import constraints
from mt5_open_close_orders import open_trade_scalping, close_trade_follow
from telegram import send_scalping_profit, send_scalping_stock


def check_gain(listAccount):
    if date.today().weekday() < 5 or (date.today().weekday() == 6 and datetime.utcnow().hour >= 22):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            account_info_dict = mt5.account_info()._asdict()
            balance = account_info_dict['balance']

            if len(openOrders) > 0:
                for order in openOrders:
                    if order.symbol != constraints.SP500_MT5 and order.symbol != constraints.DOW_MR5 \
                            and order.symbol != constraints.DAX_MT5 and order.symbol != constraints.AUS_MT5 \
                            and order.symbol != constraints.BTCUSD and order.symbol != constraints.NASDAQ_MT5 \
                            and order.symbol != constraints.FRA_MT5 and order.symbol != constraints.ESP_MT5 \
                            and order.symbol != constraints.XAUUSD:
                        if order.profit > float(
                                str((balance * (order.volume * 2) * 0.1 / 100))[:4]):
                            close_trade_follow(order.symbol, listAccount)
                            # if order.profit < float(str((balance * singleAccount["lot"] * 0.2 / 100) * -1)[:4]):
                            #     print(
                            #         " * Closing order {} in broker account {} due to loss {} is greater then {}$ :((!".format(
                            #             order.symbol, singleAccount["login"], round(order.profit, 2),
                            #             abs(balance * singleAccount["lot"] * 0.2 / 100) * -1))

                            print(
                                " * Closing order {} in broker account {} due to profit {} is greater then {}$ :))!".format(
                                    order.symbol, singleAccount["login"], abs(round(order.profit, 2)),
                                    abs(balance * (order.volume * 2) * 0.1 / 100)))


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
                if order.identifier not in listPositionIds and order.tp != 0 and order.comment == singleAccount[
                    'strategyManual']:
                    listPositionIds.append(order.identifier)
        return listPositionIds


def check_positionIds_close_orders(listAccount, listPositionIds, listCloseOrders):
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
            balance = account_info_dict['balance']
            profit = 0

            targetProfit = (balance * singleAccount["lot"] / 80)
            for order in openOrders:

                if order.comment == singleAccount["strategyShort"]:
                    profit = profit + order.profit

            if profit >= targetProfit:
                for order in openOrders:
                    if order.comment == singleAccount["strategyShort"]:
                        order_type = order.type
                        symbol = order.symbol
                        volume = order.volume

                        if order_type == mt5.ORDER_TYPE_BUY:
                            order_type = mt5.ORDER_TYPE_SELL
                            price = mt5.symbol_info_tick(symbol).bid

                        else:
                            order_type = mt5.ORDER_TYPE_BUY
                            price = mt5.symbol_info_tick(symbol).ask

                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": float(volume),
                            "type": order_type,
                            "position": order.ticket,
                            "price": price,
                            "magic": 234000,
                            "comment": singleAccount["strategyShort"],
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }

                        mt5.order_send(close_request)

                send_scalping_profit(profit)


def check_position_gain_stock(listAccount):
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
            targetProfit = (balance * singleAccount["lot"] / 400)
            for order in openOrders:

                if order.comment == singleAccount["strategyScalping"]:
                    profit = profit + order.profit

            if profit >= targetProfit:
                for order in openOrders:
                    if order.comment == singleAccount["strategyScalping"]:
                        order_type = order.type
                        symbol = order.symbol
                        volume = order.volume

                        if order_type == mt5.ORDER_TYPE_BUY:
                            order_type = mt5.ORDER_TYPE_SELL
                            price = mt5.symbol_info_tick(symbol).bid

                        else:
                            order_type = mt5.ORDER_TYPE_BUY
                            price = mt5.symbol_info_tick(symbol).ask

                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": float(volume),
                            "type": order_type,
                            "position": order.ticket,
                            "price": price,
                            "magic": 234000,
                            "comment": singleAccount["strategyShort"],
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_FOK,
                        }

                        mt5.order_send(close_request)

                send_scalping_stock(profit)