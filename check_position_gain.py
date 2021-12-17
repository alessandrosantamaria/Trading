import MetaTrader5 as mt5
from datetime import datetime
from mt5_open_close_orders import close_trade


def check_gain(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
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
                        print(" * Closing order {} in broker account {} due to loss {} is greater then {}$ :((!".format(
                            order.symbol, singleAccount["login"], round(order.profit, 2),
                            abs(balance * singleAccount["lot"] * 0.2 / 100) * -1))

                    else:
                        print(
                            " * Closing order {} in broker account {} due to profit {} is greater then {}$ :))!".format(
                                order.symbol, singleAccount["login"], abs(round(order.profit, 2)),
                                abs(balance * singleAccount["lot"] * 0.1 / 100)))
