import MetaTrader5 as mt5

from accounts import listBroker
from telegram import send_message_telegram_set_stop_loss


def update_position_stop_loss(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get()
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']

        request = {}

        for order in openOrders:
            if order.type == 1:
                price_for_stop_zero = order.price_open - abs((order.tp - order.price_open) * 2 / 3)
                order_type = 'sell'
            else:
                price_for_stop_zero = order.price_open + abs((order.tp - order.price_open) * 2 / 3)
                order_type = 'buy'

            if ((order.price_current > price_for_stop_zero and order_type == 'buy') or (
                    order.price_current < price_for_stop_zero and order_type == 'sell')) and order.sl < order.price_open:

                price = (order.price_open + order.sl) / 2

                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": order.type,
                    "position": order.ticket,
                    "price_open": order.price_open,
                    "tp": order.tp,
                    "sl": order.price_open,
                    "comment": "sent by python",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(request)
                send_message_telegram_set_stop_loss(order.symbol,order.price_open)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("[x] order_send failed, retcode={}".format(result.retcode))
                    # request the result as a dictionary and display it element by element
                    result_dict = result._asdict()
                    for field in result_dict.keys():
                        print("{}={}".format(field, result_dict[field]))
                        # if this is a trading request structure, display it element by element as well
                        if field == "request":
                            traderequest_dict = result_dict[field]._asdict()
                        #  for tradereq_filed in traderequest_dict:
                        #      print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
                else:
                    print(
                        "Stop Loss successfully placed to Initial Price for Pair {} with value {} in broker account {} for free ride :D!".format(
                            order.symbol, order.price_open, singleAccount["login"]))
        # elif order.sl < order.price_open and (
        #         order.price_current > price_for_stop_zero and order_type == 'buy') or (
        #         order.price_current < price_for_stop_zero and order_type == 'sell'):

        #     request = {
        #         "action": mt5.TRADE_ACTION_SLTP,
        #         "symbol": order.symbol,
        #         "volume": order.volume,
        #         "type": order.type,
        #         "position": order.ticket,
        #         "price_open": order.price_open,
        #         "sl": order.price_open,
        #         "tp": order.tp,
        #         "comment": "sent by python",
        #         "type_time": mt5.ORDER_TIME_GTC,
        #         "type_filling": mt5.ORDER_FILLING_IOC,
        #     }

        #     result = mt5.order_send(request)
        #     if result.retcode != mt5.TRADE_RETCODE_DONE:
        #         print("[x] order_send failed, retcode={}".format(result.retcode))
        #         # request the result as a dictionary and display it element by element
        #         result_dict = result._asdict()
        #         for field in result_dict.keys():
        #             print("{}={}".format(field, result_dict[field]))
        #             # if this is a trading request structure, display it element by element as well
        #             if field == "request":
        #                 traderequest_dict = result_dict[field]._asdict()
        #             #   for tradereq_filed in traderequest_dict:
        #             #       print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
        #     else:
        #         print(
        #             "Stop Loss successfully placed to Initial Price for Pair {} with value {} in broker account {} for free ride :D!".format(
        #                 order.symbol, order.price_open, singleAccount["login"]))


def update_position_stop_loss_to_price_open(listAccount):
    for singleAccount in listAccount:
        if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                              password=singleAccount["password"]):
            print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get()
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']

        request = {}

        for order in openOrders:

            if order.profit > float(
                    str((balance * singleAccount["lot"] * 0.075 / 100))[:4]) and order.sl == 0:

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
