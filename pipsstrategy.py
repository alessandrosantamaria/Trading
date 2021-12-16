import MetaTrader5 as mt5
from datetime import datetime
from mt5 import close_trade

def close_order_15_pips(listAccount):
    for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get()

            print("-----Check Orders for Strategy 15 Pips verification: {}-----".format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            if len(openOrders) > 0:
                for order in openOrders:
                    if (order.profit > singleAccount["15pips"] or order.profit < int(singleAccount["15pips"])*-1) and order.comment == singleAccount["commentScalping"]:
                        print("Closing order {} in broker account {} due to profit {} is greater then {}$ :))!".format(
                            order.symbol, singleAccount["login"], round(order.profit, 2),abs(singleAccount["15pips"])))
                        close_trade(order)