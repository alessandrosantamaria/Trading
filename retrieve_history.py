from datetime import datetime, date

import MetaTrader5 as mt5
import pandas as pd
from accounts import brokerFXDD50k
import operator



def retrieve_history(symbol, account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    brokerFXDD50k = {
        "login": 826838,
        "server": "BRKHoldings-Demo",
        "password": "mv7fjeql",
        "comment": "Long Run",
        "lot": 2
    }

    from_date = datetime(2020, 1, 1)
    to_date = datetime.now()
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals = mt5.history_deals_get(from_date, to_date, group=symbol)
    dict_deals = []
    for deal in deals:
        dict = {'time': deal.time, 'symbol': deal.symbol, 'profit': deal.profit, 'order': deal.order}
        if dict['profit'] != 0.0:
            dict_deals.append(dict)
        dict_deals.sort(key=lambda item: item.get("order"))

    return dict_deals[0]



