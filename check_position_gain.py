from datetime import date, datetime

import MetaTrader5 as mt5

from accounts import listBroker
from mt5_open_close_orders import close_trade


def check_gain(listAccount):
    if date.today().weekday() < 5 or (date.today().weekday() == 6 and datetime.now().hour >= 23):
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
                    if order.profit < float(
                            str((balance * singleAccount["lot"] * 0.2 / 100) * -1)[:4]) or order.profit > float(
                        str((balance * singleAccount["lot"] * 0.1 / 100))[:4]):
                        close_trade(order.symbol, listAccount)
                        if order.profit < float(str((balance * singleAccount["lot"] * 0.2 / 100) * -1)[:4]):
                            print(
                                " * Closing order {} in broker account {} due to loss {} is greater then {}$ :((!".format(
                                    order.symbol, singleAccount["login"], round(order.profit, 2),
                                    abs(balance * singleAccount["lot"] * 0.2 / 100) * -1))

                        else:
                            print(
                                " * Closing order {} in broker account {} due to profit {} is greater then {}$ :))!".format(
                                    order.symbol, singleAccount["login"], abs(round(order.profit, 2)),
                                    abs(balance * singleAccount["lot"] * 0.1 / 100)))


def retrieve_position_ids(listAccount, listPositionIds):
    if date.today().weekday() < 5 or (date.today().weekday() == 6 and datetime.now().hour >= 23):
        for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()

        openOrders = mt5.positions_get()
        if len(openOrders) > 0:
            for order in openOrders:
                if order.identifier not in listPositionIds:
                    listPositionIds.append(order.identifier)
        return listPositionIds


def check_positionIds_close_orders(listAccount, listPositionIds, listCloseOrders):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                  mt5.last_error())
            quit()
        if date.today().weekday() < 5:
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
