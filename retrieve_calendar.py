import csv

from datetime import datetime

import mt5

import constraints
from accounts import broker, listBroker


def retrieve_calendar(date):
    csvFilePath = 'calendar-event-list.csv'

    data = []
    booleanFound = False
    with open(csvFilePath) as csvFile:
        csvReader = csv.DictReader(csvFile)
        for rows in csvReader:
            date_time_str = rows['Start']
            date_time_obj = datetime.strptime(date_time_str, '%m/%d/%Y %H:%M:%S')
            rows['Start'] = date_time_obj.date()
            dict = {
                'Id': rows['Id'],
                'Start': date_time_obj.date(),
                'Name': rows['Name'],
                'Impact': rows['Impact'],
                'Currency': rows['Currency']
            }
            data.append(dict)
    constraints.eventFound
    for x in data:
        if x['Start'] == date and x['Name'] in ('Nonfarm Payrolls', 'Fed Interest Rate Decision'):
            booleanFound = True
    if booleanFound:
        constraints.eventFound = True
    else:
        constraints.eventFound = False


def close_all_profit_and_no_trading(listBroker, date):
    for singleAccount in listBroker:
        print("\n-----Check Economic Calendar: {}-----\n".format(
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        retrieve_calendar(date)
        print("Event Found : {}".format(constraints.eventFound))
        if constraints.eventFound:
            if not mt5.initialize(login=singleAccount["login"], server=singleAccount["server"],
                                  password=singleAccount["password"]):
                print("initialize() failed for account {} , error code =".format(singleAccount["login"]),
                      mt5.last_error())
                quit()


            openOrders = mt5.positions_get()
            for order in openOrders:

                order_type = order.type
                symbol = order.symbol
                volume = order.volume

                if order_type == mt5.ORDER_TYPE_BUY:
                    order_type = mt5.ORDER_TYPE_SELL
                    price = mt5.symbol_info_tick(symbol).bid
                else:
                    order_type = mt5.ORDER_TYPE_BUY
                    price = mt5.symbol_info_tick(symbol).ask

                if symbol == constraints.BTC_MT5:
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
