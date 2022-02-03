from enum import Enum

import constraints
from accounts import listBroker
from mt5_open_close_orders import  open_trade_manual


class Action(Enum):
    Buy = "BUY"
    Sell = "SELL"


symbol = constraints.EURCHF
action = Action.Buy.value
lot = 1

if "JPY" in symbol:
    sizeRenko = 0.1
elif "ZAR" in symbol:
    sizeRenko = 0.03
elif "XAUUSD" in symbol:
    sizeRenko = 2
elif "BTC" in symbol:
    sizeRenko = 500
elif "500" in symbol:
    sizeRenko = 5
elif "100" in symbol:
    sizeRenko = 25
elif "30" in symbol:
    sizeRenko = 40
elif "GER" in symbol:
    sizeRenko = 30
else:
    sizeRenko = 0.001

open_trade_manual(action, symbol, listBroker, sizeRenko, lot)
