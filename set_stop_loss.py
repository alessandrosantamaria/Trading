import MetaTrader5 as mt5
from datetime import datetime


def update_position_take_profit(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get()
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']
        print("-----Check Orders for Strategy Long Run verification: {}-----".format(
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        request = {}

        for order in openOrders:

            if order.profit > balance * 1 / 100:
                price = (order.price_open + order.price_current) / 2

                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": order.type,
                    "position": order.ticket,
                    "price_open": order.price_open,
                    "sl": price,
                    "comment": "sent by python",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                if order.type == 1:

                    if order.sl > 0 and price >= order.sl:
                        break
                else:

                    if order.sl > 0 and price <= order.sl:
                        break
                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("[x] order_send failed, retcode={}".format(result.retcode))
                    # request the result as a dictionary and display it element by element
                    result_dict = result._asdict()
                    for field in result_dict.keys():
                        print("{}={}".format(field, result_dict[field]))
                        # if this is a trading request structure, display it element by element as well
                        if field == "request":
                            traderequest_dict = result_dict[field]._asdict()
                            for tradereq_filed in traderequest_dict:
                                print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
                else:
                    print("Stop Loss successfully placed for Pair {} with value {} in broker account {} for an "
                          "estimated return of {}$!".format(
                        order.symbol, price, singleAccount["login"], round(order.profit / 2, 2)))
            elif order.sl != order.price_open and order.profit > balance * 0.5 / 100 and order.profit < balance * 1 / 100:

                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": order.type,
                    "position": order.ticket,
                    "price_open": order.price_open,
                    "sl": order.price_open,
                    "comment": "sent by python",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("[x] order_send failed, retcode={}".format(result.retcode))
                    # request the result as a dictionary and display it element by element
                    result_dict = result._asdict()
                    for field in result_dict.keys():
                        print("{}={}".format(field, result_dict[field]))
                        # if this is a trading request structure, display it element by element as well
                        if field == "request":
                            traderequest_dict = result_dict[field]._asdict()
                            for tradereq_filed in traderequest_dict:
                                print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
                else:
                    print(
                        "Stop Loss successfully placed to Initial Price for Pair {} with value {} in broker account {} for free ride :D!".format(
                            order.symbol, order.price_open, singleAccount["login"], round(order.profit / 2, 2)))
