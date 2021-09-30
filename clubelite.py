import enum

import mt5 as mt5

from main import listBroker
import MetaTrader5 as mt5


class Symbol(enum.Enum):
    EUR = "EURUSD"
    GBP = "GBPUSD"
    CAD = 'USDCAD'
    NZD = "NZDUSD"
    JPY = "USDJPY"
    AUD = "AUDUSD"
    DAX = "GER.30"
    SPX500 = "SPX500"


class Operation(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


elitè = {
    "target": 1.1548,
    "symbol": Symbol.EUR,
    "action": Operation.SELL
}


def club_elite_execution(elitè, listBroker):
    for singleBroker in listBroker:

        if not mt5.initialize(login=singleBroker["login"], server=singleBroker["server"], password=singleBroker["password"]):
            print("initialize() failed for account {} , error code =".format(singleBroker["login"]), mt5.last_error())
            quit()


        if elitè["action"].value == 'BUY':
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(elitè["symbol"].value).ask


        elif elitè["action"].value == 'SELL':
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(elitè["symbol"].value).bid


        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": elitè["symbol"].value,
            "volume": singleBroker["clubEliteSize"],
            "tp": elitè["target"],
            "type": trade_type,
            "price": price,
            "magic": 9986989,
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

            print("Club Elitè: Order successfully placed in broker account {}!".format(singleBroker["login"]))


club_elite_execution(elitè, listBroker)
