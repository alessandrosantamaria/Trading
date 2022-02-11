import MetaTrader5 as mt5
from datetime import datetime

from constraints import BTC_MT5, LONG_STRATEGY


def close_all_trade_with_profit(singleAccount):
    if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                          password=singleAccount["password"]):
        print("initialize() failed for account {} , error code =".format(singleAccount["login"]), mt5.last_error())
        quit()
    print("\n-----Check Orders for Take profit for All positions verification: {}-----\n".format(
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    account_info_dict = mt5.account_info()._asdict()
    balance = account_info_dict['balance']
    openOrders = mt5.positions_get()
    for order in openOrders:
        if order.comment == LONG_STRATEGY:
            print(
                "Closing order {} in broker account {} since that the sum of all trades {} are greater then {}!".format(
                    order.symbol, singleAccount["login"], account_info_dict['profit'], balance * 0.05))
            order_type = order.type
            symbol = order.symbol
            volume = order.volume
            action = ''

            if order_type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
                action = 'BUY'
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
                action = 'SELL'

            if symbol == BTC_MT5:
                typeFilling = mt5.ORDER_FILLING_FOK
            else:
                typeFilling = mt5.ORDER_FILLING_IOC

            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "position": order.ticket,
                "price": price,
                "magic": 234000,
                "comment": order.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": typeFilling,
            }

            mt5.order_send(close_request)
