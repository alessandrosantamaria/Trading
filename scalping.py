import MetaTrader5 as mt5
from datetime import datetime
from mt5 import close_trade

ea_magic_number = 9986989

def scalping_strategy(action, symbol, listBroker):
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
            tp = price + 50 * point
            sl = price - 70 * point

        elif action == 'SELL':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            point = mt5.symbol_info(symbol).point
            tp = price - 50 * point
            sl = price + 70 * point




        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": i["sizeScalping"],
            "tp": tp,
           # "sl" : sl,
            "type": trade_type,
            "price": price,
            "magic": ea_magic_number,
            "comment": i["commentScalping"],
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
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