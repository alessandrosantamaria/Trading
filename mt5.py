import MetaTrader5 as mt5


ea_magic_number = 9986989 # if you want to give every bot a unique identifier

def get_info(symbol):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5symbolinfo_py
    '''
    # get symbol properties
    info=mt5.symbol_info(symbol)
    return info


def open_trade(action, symbol, lot):

    orders1 = mt5.positions_get(symbol=symbol)
    if len(orders1) > 0:
        close_trade(orders1[0])



    if action == 'BUY':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif action =='SELL':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point

    buy_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": price,
       # "sl": price - sl_points * point,
       # "tp": price + tp_points * point,
        "magic": ea_magic_number,
        "comment": "sent by python",
        "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
        "type_filling": mt5.ORDER_FILLING_IOC,
    }


    # send a trading request
    result = mt5.order_send(buy_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
    else:
        print("Order successfully placed!")
    return result, buy_request

def close_trade(order):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
    '''
    # create a close request

    order_type = order.type
    symbol = order.symbol
    volume = order.volume

    if (order_type == mt5.ORDER_TYPE_BUY):
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



    # send a close request
    result=mt5.order_send(close_request)


# This is how I would execute the order

if not mt5.initialize(login=2100036944,server="FXDD-Demo",password="z2cfifrb"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()


