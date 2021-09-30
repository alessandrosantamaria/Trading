import MetaTrader5 as mt5
from datetime import datetime
from mt5 import close_trade

def close_order_15_pips(listAccount):

            if not mt5.initialize(login=listAccount["login"], server=listAccount["server"],
                                  password=listAccount["password"]):
                print("initialize() failed for account {} , error code =".format(listAccount["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            print("-----Check Orders for Strategy 15 Pips verification: {}-----".format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            if len(openOrders) > 0:
                for order in openOrders:
                    if order.profit > listAccount["15pips"]:
                        print("Closing order {} in broker account {} due to profit {} is greater then {}$ :))!".format(
                            order.symbol, listAccount["login"], round(order.profit, 2),abs(listAccount["15pips"])))
                        close_trade(order)