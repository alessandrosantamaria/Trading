import datetime

import mt5

from accounts import listBroker
from constraints import *


def check_position_scalping(listAccount,strategy):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()
        datetime.datetime.utcnow()
        openOrders = mt5.positions_get()
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']
        profit = 0
        for order in openOrders:
            if order.comment == strategy:
                profit = profit + order.profit
        if strategy == SHORT_STRATEGY:
             print("Strategy {}:\nActual Profit: {} - Target: {}".format(strategy,round(profit,2),round((balance * singleAccount["lot"] / 40),2)))
        elif strategy == LONG_STRATEGY:
            print("Strategy {}:\nActual Profit: {} - Target: {}".format(strategy,round(profit, 2), round((balance * singleAccount["lot"] / 20),2)))
        else:
            print("Strategy {}:\nActual Profit: {} - Target: {}".format(strategy,round(profit, 2), round((balance * singleAccount["lot"] / 200),2)))


check_position_scalping(listBroker,SHORT_STRATEGY)
check_position_scalping(listBroker,LONG_STRATEGY)
check_position_scalping(listBroker, SCALPING_STRATEGY)