import MetaTrader5 as mt5
from datetime import datetime
from mt5 import close_trade


def close_order_limit_loss(listAccount):
    for singleAccount in listAccount:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
                quit()

            openOrders = mt5.positions_get()
            print(
                "-----Check Orders for Close Order verification: {}-----".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            if len(openOrders) > 0:
                for order in openOrders:
                    if order.profit < singleAccount["closeOrderLimit"]:
                        print("Closing order {} in broker account {} due to loss {} is greater then {}$ :((!".format(
                            order.symbol, singleAccount["login"], abs(round(order.profit, 2)),abs(singleAccount["closeOrderLimit"])))
                        close_trade(order)


