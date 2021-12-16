import MetaTrader5 as mt5
from datetime import datetime

from mt5 import close_trade


def close_all_trade_with_profit(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()
        print("\n-----Check Orders for Take profit for All positions verification: {}-----\n".format(
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']
        if account_info_dict['profit'] > balance * 0.1:
            openOrders = mt5.positions_get()
            for order in openOrders:
                print(
                    "Closing order {} in broker account {} since that the sum of all trades {} are greater then {}!".format(
                        order.symbol, singleAccount["login"],account_info_dict['profit'], balance * 0.05))
                close_trade(order.symbol, listAccount)
