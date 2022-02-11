from datetime import datetime, date, timedelta
import MetaTrader5 as mt5

from accounts import broker
from constraints import *


def retrieve_history_by_symbol(symbol, account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    from_date = datetime(2020, 1, 1)
    to_date = datetime.now() + timedelta(days=1)
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals = mt5.history_deals_get(from_date, to_date, group=symbol)
    dict_deals = []
    for deal in deals:
        dict = {'time': deal.time, 'symbol': deal.symbol, 'profit': deal.profit, 'order': deal.order}
        if dict['profit'] != 0.0:
            dict_deals.append(dict)
        dict_deals.sort(key=lambda item: item.get("order"))

    return dict_deals


def sum_results_trades(listTrades, symbol):
    total_profit = 0
    for trade in listTrades:
        total_profit = total_profit + trade["profit"]
    if total_profit > 0 or total_profit < 0:
        print("*********")
        print("The sum of all trades profit for the symbol {} is {}$".format(symbol, round(total_profit, 2)))
        print("*********")


def sum_results_trades_sessions(listTrades, symbol):
    total_profit_london = 0
    total_profit_usa = 0
    total_profit_no_session = 0
    for trade in listTrades:
        if datetime.fromtimestamp(trade['time']).hour >= 9 and datetime.fromtimestamp(trade['time']).hour < 14:
            total_profit_london = total_profit_london + trade["profit"]
        elif datetime.fromtimestamp(trade['time']).hour >= 14 and datetime.fromtimestamp(trade['time']).hour < 21:
            total_profit_london = total_profit_london + trade["profit"]
        else:
            total_profit_no_session = total_profit_no_session + trade["profit"]
    if total_profit_london > 0 or total_profit_london < 0 or total_profit_usa > 0 or total_profit_usa < 0 or total_profit_no_session > 0 or total_profit_no_session < 0:
        print("*********")
        print("The sum of all trades profit for London Session for the symbol {} is {}$".format(symbol,
                                                                                                round(
                                                                                                    total_profit_london,
                                                                                                    2)))
        print("The sum of all trades profit for USA Session for the symbol {} is {}$".format(symbol, round(
            total_profit_usa, 2)))
        print("The sum of all trades profit for Other Sessions for the symbol {} is {}$".format(symbol, round(
            total_profit_no_session, 2)))
        print("*********")


def daily_report(account, strategy):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    from_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day - 1)
    to_date = datetime.now()
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals = mt5.history_deals_get(from_date, to_date)
    dict_deals = []

    for deal in deals:
        if deal.comment != 'Deposit':
            dict = {'position_id': deal.position_id, 'time': deal.time, 'symbol': deal.symbol,
                    'profit': deal.profit, 'order': deal.order, 'volume': deal.volume}
            if dict['profit'] != 0.0:
                orders = mt5.history_orders_get(position=dict['position_id'])
                for order in orders:
                    if order.comment == strategy:
                        dict['comment'] = order.comment
                        dict_deals.append(dict)
                        break
            dict_deals.sort(key=lambda item: item.get("order"))
    number_trades_profit = 0
    profit = 0
    loss = 0
    number_trades_loss = 0
    for trade in dict_deals:
        if trade['profit'] > 0:
            number_trades_profit = number_trades_profit + 1
            profit = trade['profit'] + profit
        elif trade['profit'] < 0:
            number_trades_loss = number_trades_loss + 1
            loss = loss + trade['profit']
    account_info_dict = mt5.account_info()._asdict()
    balance = account_info_dict['balance']
    message = 'Report {} {}\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\nBalance : {}'.format(
        strategy,
        from_date.date(),
        number_trades_profit, round(profit, 2),

        number_trades_loss,
        loss,
        round(profit + loss, 2),
        balance)
    return message


def sum_results_for_all_symbols(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    symbols = mt5.symbols_get()
    for symbol in symbols:
        listTrades = retrieve_history_by_symbol(symbol.name, account)
        sum_results_trades(listTrades, symbol.name)


def sum_results_for_forex_symbol(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    symbols = mt5.symbols_get()
    number_trades_profit = 0
    profit = 0
    loss = 0
    number_trades_loss = 0
    for symbol in symbols:
        if symbol.name != DAX_MT5 and symbol.name != NASDAQ_MT5 and symbol.name != SP500_MT5 and symbol.name != DOW_MR5 and symbol.name != BTC_MT5 and symbol.name != FRA_MT5 and symbol.name != ESP_MT5 and symbol.name != AUS_MT5 and symbol.name != XAUUSD:
            listTrades = retrieve_history_by_symbol(symbol.name, account)
            for trade in listTrades:
                if trade['profit'] > 0:
                    number_trades_profit = number_trades_profit + 1
                    profit = trade['profit'] + profit
                else:
                    number_trades_loss = number_trades_loss + 1
                    loss = loss + trade['profit']
    print("******")
    print("The number of positive trades are {}".format(number_trades_profit))
    print("The profit of trades is {}".format(profit))
    print("The number of negative trades are {}".format(number_trades_loss))
    print("The loss of trades is {}".format(loss))
    print("******")


def sum_results_for_index_symbol(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    symbols = mt5.symbols_get()
    number_trades_profit = 0
    profit = 0
    loss = 0
    number_trades_loss = 0
    for symbol in symbols:
        if symbol.name == DAX_MT5 or symbol.name == NASDAQ_MT5 or symbol.name == SP500_MT5 or symbol.name == DOW_MR5 or symbol.name == BTC_MT5 or symbol.name == FRA_MT5 or symbol.name == ESP_MT5 or symbol.name == AUS_MT5 or symbol.name == XAUUSD:
            listTrades = retrieve_history_by_symbol(symbol.name, account)
            for trade in listTrades:
                if trade['profit'] > 0:
                    number_trades_profit = number_trades_profit + 1
                    profit = trade['profit'] + profit
                else:
                    number_trades_loss = number_trades_loss + 1
                    loss = loss + trade['profit']
    print("******")
    print("The number of positive trades are {}".format(number_trades_profit))
    print("The profit of trades is {}".format(profit))
    print("The number of negative trades are {}".format(number_trades_loss))
    print("The loss of trades is {}".format(loss))
    print("******")


def sum_results_for_all_symbols_by_session(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    symbols = mt5.symbols_get()
    for symbol in symbols:
        listTrades = retrieve_history_by_symbol(symbol.name, account)
        sum_results_trades_sessions(listTrades, symbol.name)


def historical_report(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    from_date = datetime(2021, 2, 10)
    to_date = datetime.now()
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals = mt5.history_deals_get(from_date, to_date)
    dates = []
    total_number_trades_profit = 0
    total_profit = 0
    total_loss = 0
    total_number_trades_loss = 0
    total_number_trades_profit_manual = 0
    total_profit_manual = 0
    total_loss_manual = 0
    total_number_trades_loss_manual = 0
    total_number_trades_profit_stock = 0
    total_profit_stock = 0
    total_loss_stock = 0
    total_number_trades_loss_stock = 0
    total_number_trades_profit_personal = 0
    total_profit_personal = 0
    total_loss_personal = 0
    total_number_trades_loss_personal = 0
    for deal in deals:
        dict = {'time': deal.time, 'symbol': deal.symbol, 'profit': deal.profit, 'order': deal.order}
        if datetime.fromtimestamp(dict['time']).date() not in dates:
            dates.append(datetime.fromtimestamp(dict['time']).date())

    for date in dates:
        from_date = datetime(date.year, date.month, date.day)
        to_date = from_date + timedelta(days=1)
        # get deals for symbols whose names contain "GBP" within a specified interval
        deals = mt5.history_deals_get(from_date, to_date)
        dict_deals = []
        number_trades_profit_follow = 0
        profit_follow = 0
        loss_follow = 0
        number_trades_loss_follow = 0
        number_trades_profit_manual = 0
        profit_manual = 0
        loss_manual = 0
        number_trades_loss_manual = 0
        number_trades_profit_stock = 0
        profit_stock = 0
        loss_stock = 0
        number_trades_loss_stock = 0
        number_trades_profit_personal = 0
        profit_personal = 0
        loss_personal = 0
        number_trades_loss_personal = 0
        for deal in deals:
            if deal.comment != 'Deposit':
                dict = {'position_id': deal.position_id, 'time': deal.time, 'symbol': deal.symbol,
                        'profit': deal.profit, 'order': deal.order, 'volume': deal.volume}
                if dict['profit'] != 0.0:
                    orders = mt5.history_orders_get(position=dict['position_id'])
                    for order in orders:
                        if order.comment == LONG_STRATEGY or order.comment == SCALPING_STRATEGY or order.comment == SHORT_STRATEGY or 'tp' in order.comment:
                            dict['comment'] = order.comment
                            dict_deals.append(dict)
                            break
                dict_deals.sort(key=lambda item: item.get("order"))
        for trade in dict_deals:
            if trade['profit'] > 0 and trade['symbol'] != '' and trade['comment'] == LONG_STRATEGY:
                number_trades_profit_follow = number_trades_profit_follow + 1
                profit_follow = trade['profit'] + profit_follow
                total_number_trades_profit = total_number_trades_profit + 1
                total_profit = total_profit + trade['profit']
            elif trade['profit'] < 0 and trade['symbol'] != '' and trade['comment'] == LONG_STRATEGY:
                number_trades_loss_follow = number_trades_loss_follow + 1
                loss_follow = loss_follow + trade['profit']
                total_number_trades_loss = total_number_trades_loss + 1
                total_loss = total_loss + trade['profit']
            elif trade['profit'] > 0 and trade['symbol'] != '' and trade['comment'] == SHORT_STRATEGY:
                number_trades_profit_manual = number_trades_profit_manual + 1
                profit_manual = trade['profit'] + profit_manual
                total_number_trades_profit_manual = total_number_trades_profit_manual + 1
                total_profit_manual = trade['profit'] + total_profit_manual
            elif trade['profit'] < 0 and trade['symbol'] != '' and trade['comment'] == SHORT_STRATEGY:
                number_trades_loss_manual = number_trades_loss_manual + 1
                loss_manual = loss_manual + trade['profit']
                total_number_trades_loss_manual = total_number_trades_loss_manual + 1
                total_loss_manual = total_loss_manual + trade['profit']
            elif trade['profit'] > 0 and trade['symbol'] != '' and trade['comment'] == SCALPING_STRATEGY:
                number_trades_profit_stock = number_trades_profit_stock + 1
                profit_stock = trade['profit'] + profit_stock
                total_number_trades_profit_stock = total_number_trades_profit_stock + 1
                total_profit_stock = trade['profit'] + total_profit_stock
            elif trade['profit'] < 0 and trade['symbol'] != '' and trade['comment'] == SCALPING_STRATEGY:
                number_trades_loss_stock = number_trades_loss_stock + 1
                loss_stock = loss_stock + trade['profit']
                total_number_trades_loss_stock = total_number_trades_loss_stock + 1
                total_loss_stock = total_loss_stock + trade['profit']
            elif trade['profit'] > 0 and trade['symbol'] != '' and 'tp' in trade['comment']:
                number_trades_profit_personal = number_trades_profit_personal + 1
                profit_personal = trade['profit'] + profit_personal
                total_number_trades_profit_personal = total_number_trades_profit_personal + 1
                total_profit_personal = trade['profit'] + total_profit_personal
            elif trade['profit'] < 0 and trade['symbol'] != '' and 'tp' in trade['comment']:
                number_trades_loss_personal = number_trades_loss_personal + 1
                loss_personal = loss_personal + trade['profit']
                total_number_trades_loss_personal = total_number_trades_loss_personal + 1
                total_loss_personal = total_loss_personal + trade['profit']
        print("Date {}\n".format(from_date.date()))
        print(
            'Report Follow Strategy:\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

                number_trades_profit_follow, round(profit_follow, 2),

                number_trades_loss_follow,
                round(loss_follow, 2),
                round(profit_follow + loss_follow, 2)
            ))
        print(
            'Report Momentum Strategy:\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

                number_trades_profit_manual, round(profit_manual, 2),
                number_trades_loss_manual,
                round(loss_manual, 2),
                round(profit_manual + loss_manual, 2)
            ))
        print(
            'Report Scalping Strategy:\nNumber Trades in Profit Scalping : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

                number_trades_profit_stock, round(profit_stock, 2),
                number_trades_loss_stock,
                round(loss_stock, 2),
                round(profit_stock + loss_stock, 2)
            ))
        print(
            'Report Manual Strategy:\nNumber Trades in Profit Scalping : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

                number_trades_profit_personal, round(profit_personal, 2),
                number_trades_loss_personal,
                round(loss_personal, 2),
                round(profit_personal + loss_personal, 2)
            ))
    print("**********************************")
    print(
        'Report Total Follow Strategy:\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit, round(total_profit, 2),
            total_number_trades_loss,
            round(total_loss, 2),
            round(total_profit + total_loss, 2)
        ))
    print(
        'Report Total Momentum Strategy:\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit_manual, round(total_profit_manual, 2),
            total_number_trades_loss_manual,
            round(total_loss_manual, 2),
            round(total_profit_manual + total_loss_manual, 2)
        ))
    print(
        'Report Total Scalping Strategy:\nNumber Trades in Profit Scalping : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit_stock, round(total_profit_stock, 2),
            total_number_trades_loss_stock,
            round(total_loss_stock, 2),
            round(total_profit_stock + total_loss_stock, 2)
        ))
    print(
        'Report Total Manual Strategy:\nNumber Trades in Profit Scalping : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit_personal, round(total_profit_personal, 2),
            total_number_trades_loss_personal,
            round(total_loss_personal, 2),
            round(total_profit_personal + total_loss_personal, 2)
        ))
    print("**********************************")


def report_telegram(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    from_date = datetime(2021, 2, 10)
    to_date = datetime.now()
    message = []
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals = mt5.history_deals_get(from_date, to_date)
    dates = []
    total_number_trades_profit = 0
    total_profit = 0
    total_loss = 0
    total_number_trades_loss = 0
    total_number_trades_profit_manual = 0
    total_profit_manual = 0
    total_loss_manual = 0
    total_number_trades_loss_manual = 0
    total_number_trades_profit_stock = 0
    total_profit_stock = 0
    total_loss_stock = 0
    total_number_trades_loss_stock = 0
    total_number_trades_profit_personal = 0
    total_profit_personal = 0
    total_loss_personal = 0
    total_number_trades_loss_personal = 0
    for deal in deals:
        dict = {'time': deal.time, 'symbol': deal.symbol, 'profit': deal.profit, 'order': deal.order}
        if datetime.fromtimestamp(dict['time']).date() not in dates:
            dates.append(datetime.fromtimestamp(dict['time']).date())

    for date in dates:
        from_date = datetime(date.year, date.month, date.day)
        to_date = from_date + timedelta(days=1)
        # get deals for symbols whose names contain "GBP" within a specified interval
        deals = mt5.history_deals_get(from_date, to_date)
        dict_deals = []
        for deal in deals:
            if deal.comment != 'Deposit':
                dict = {'position_id': deal.position_id, 'time': deal.time, 'symbol': deal.symbol,
                        'profit': deal.profit, 'order': deal.order, 'volume': deal.volume}
                if dict['profit'] != 0.0:
                    orders = mt5.history_orders_get(position=dict['position_id'])
                    for order in orders:
                        if order.comment == LONG_STRATEGY or order.comment == SCALPING_STRATEGY or order.comment == SHORT_STRATEGY or 'tp' in order.comment:
                            dict['comment'] = order.comment
                            dict_deals.append(dict)
                            break
                dict_deals.sort(key=lambda item: item.get("order"))
        for trade in dict_deals:
            if trade['profit'] > 0 and trade['symbol'] != '' and trade['comment'] == LONG_STRATEGY:
                total_number_trades_profit = total_number_trades_profit + 1
                total_profit = total_profit + trade['profit']
            elif trade['profit'] < 0 and trade['symbol'] != '' and trade['comment'] == LONG_STRATEGY:
                total_number_trades_loss = total_number_trades_loss + 1
                total_loss = total_loss + trade['profit']
            elif trade['profit'] > 0 and trade['symbol'] != '' and trade['comment'] == SHORT_STRATEGY:
                total_number_trades_profit_manual = total_number_trades_profit_manual + 1
                total_profit_manual = trade['profit'] + total_profit_manual
            elif trade['profit'] < 0 and trade['symbol'] != '' and trade['comment'] == SHORT_STRATEGY:
                total_number_trades_loss_manual = total_number_trades_loss_manual + 1
                total_loss_manual = total_loss_manual + trade['profit']
            elif trade['profit'] > 0 and trade['symbol'] != '' and trade['comment'] == SCALPING_STRATEGY:
                total_number_trades_profit_stock = total_number_trades_profit_stock + 1
                total_profit_stock = trade['profit'] + total_profit_stock
            elif trade['profit'] < 0 and trade['symbol'] != '' and trade['comment'] == SCALPING_STRATEGY:
                total_number_trades_loss_stock = total_number_trades_loss_stock + 1
                total_loss_stock = total_loss_stock + trade['profit']
            elif trade['profit'] > 0 and trade['symbol'] != '' and 'tp' in trade['comment']:
                total_number_trades_profit_personal = total_number_trades_profit_personal + 1
                total_profit_personal = trade['profit'] + total_profit_personal
            elif trade['profit'] < 0 and trade['symbol'] != '' and 'tp' in trade['comment']:
                total_number_trades_loss_personal = total_number_trades_loss_personal + 1
                total_loss_personal = total_loss_personal + trade['profit']

    message.append(
        'Report Total Follow Strategy:\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit, round(total_profit, 2),
            total_number_trades_loss,
            round(total_loss, 2),
            round(total_profit + total_loss, 2)
        ))
    message.append(
        'Report Total Momentum Strategy:\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit_manual, round(total_profit_manual, 2),
            total_number_trades_loss_manual,
            round(total_loss_manual, 2),
            round(total_profit_manual + total_loss_manual, 2)
        ))
    message.append(
        'Report Total Scalping Strategy:\nNumber Trades in Profit Scalping : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit_stock, round(total_profit_stock, 2),
            total_number_trades_loss_stock,
            round(total_loss_stock, 2),
            round(total_profit_stock + total_loss_stock, 2)
        ))
    message.append(
        'Report Total Manual Strategy:\nNumber Trades in Profit Scalping : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nNet Trades {}\n'.format(

            total_number_trades_profit_personal, round(total_profit_personal, 2),
            total_number_trades_loss_personal,
            round(total_loss_personal, 2),
            round(total_profit_personal + total_loss_personal, 2)
        ))

    return message
