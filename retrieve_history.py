from datetime import datetime, date, timedelta
import MetaTrader5 as mt5

def retrieve_history_by_symbol(symbol, account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    from_date = datetime(2020, 1, 1)
    to_date = datetime.now()
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
    print("*********")
    print("The sum of all trades profit for London Session for the symbol {} is {}$".format(symbol,
                                                                                            round(total_profit_london,
                                                                                                  2)))
    print("The sum of all trades profit for USA Session for the symbol {} is {}$".format(symbol, round(
        total_profit_usa, 2)))
    print("The sum of all trades profit for Other Sessions for the symbol {} is {}$".format(symbol, round(
        total_profit_no_session, 2)))
    print("*********")


def daily_report(account):
    if not mt5.initialize(login=account["login"], server=account["server"], password=account["password"]):
        print("initialize() failed for account {} , error code =".format(account), mt5.last_error())
        quit()
    from_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day - 1)
    to_date = datetime.now()
    # get deals for symbols whose names contain "GBP" within a specified interval
    deals = mt5.history_deals_get(from_date, to_date)
    dict_deals = []
    for deal in deals:
        dict = {'time': deal.time, 'symbol': deal.symbol, 'profit': deal.profit, 'order': deal.order}
        if dict['profit'] != 0.0:
            dict_deals.append(dict)
        dict_deals.sort(key=lambda item: item.get("order"))
    number_trades_profit = 0
    profit = 0
    loss = 0
    number_trades_loss = 0
    for trade in dict_deals:
        if trade['profit'] > 0:
            number_trades_profit = number_trades_profit + 1
            profit = trade['profit'] + profit
        else:
            number_trades_loss = number_trades_loss + 1
            loss = loss + trade['profit']
    account_info_dict = mt5.account_info()._asdict()
    balance = account_info_dict['balance']
    message = 'Report {}\nNumber Trades in Profit : {}\nProfit : {}\nNumber Trades in Loss : {}\nLoss : {}\nBalance : {}'.format(
        from_date.date(),
        number_trades_profit, profit,

        number_trades_loss,
        loss,
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


