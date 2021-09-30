import MetaTrader5 as mt5

ea_magic_number = 9986989  # if you want to give every bot a unique identifier


def get_info(symbol):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5symbolinfo_py
    '''
    # get symbol properties
    info = mt5.symbol_info(symbol)
    return info


def open_trade(action, symbol, listBroker):
    for i in listBroker:

        if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
            print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
            quit()

        openOrders = mt5.positions_get(symbol=symbol)
        if len(openOrders) > 0:
            close_trade(openOrders[0])

        if action == 'BUY':
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
            point = mt5.symbol_info(symbol).point
            tp = price + 150 * point
        elif action == 'SELL':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            point = mt5.symbol_info(symbol).point
            tp = price - 150 * point

        if "XAU" in symbol:
            lot = i["sizeXau"]
        elif "ZAR" in symbol:
            lot = i["sizeZar"]
        else:
            lot = i["size"]

        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            #  "tp": tp,
            "type": trade_type,
            "price": price,
            "magic": ea_magic_number,
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
                        print("traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))

        else:

            print("Order successfully placed in broker account {}!".format(i["login"]))



def close_trade(order):
    order_type = order.type
    symbol = order.symbol
    volume = order.volume

    if order_type == mt5.ORDER_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": order.ticket,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    mt5.order_send(close_request)
