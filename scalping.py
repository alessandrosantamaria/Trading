import MetaTrader5 as mt5
from datetime import datetime
from mt5 import close_trade


def scalping_strategy(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get()
        print(
            "-----Check Orders for Scalping Strategy: {}-----".format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        if len(openOrders) > 0:
            for order in openOrders:
                if order.profit > singleAccount["scalpingTarget"]:
                    print("Closing order {} in broker account {} due to greater then {}$ :))!".format(
                        order.symbol, singleAccount["login"], abs(round(order.profit, 2))))
                    close_trade(order)
                    if order.type == 1:
                        price = mt5.symbol_info_tick(order.symbol).ask
                        point = mt5.symbol_info(order.symbol).point
                    else:
                        price = mt5.symbol_info_tick(order.symbol).bid

                    buy_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": order.symbol,
                        "volume": order.volume,
                        "type": order.type,
                        "price": price,
                        "magic": 13124341,
                        "comment": "sent by python",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    # send a trading request
                    result = mt5.order_send(buy_request)
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
                                    print("traderequest: {}={}".format(tradereq_filed,
                                                                       traderequest_dict[tradereq_filed]))
                    else:
                        print("Order successfully replaced in broker account {} for pair {}!".format(
                            singleAccount["login"], order.symbol))
