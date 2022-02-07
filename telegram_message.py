import requests
import MetaTrader5 as mt5

from accounts import listBroker
from constraints import *
from retrieve_history import daily_report



def send_message_telegram_open_trade(symbol, lot, action,strategy):
    message = '** Open Trade **\nSymbol: {}\nLot: {}\nAction: {}\nStrategy: {}\n{}'.format(symbol, lot, action,strategy,
                                                                             '\N{call me hand}')
    requests.post(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                               message))


def send_message_telegram_close_trade(symbol, profit):
    if profit > 0:
        message = '** Close Trade **\nSymbol: {}\nProfit: {}$\n{}'.format(symbol, profit,
                                                                          '\N{money-mouth face}')
    else:
        message = '** Close Trade **\nSymbol: {}\nLoss: {}$\n{}'.format(symbol, profit,
                                                                        '\N{loudly crying face}')
    requests.post(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                               message))


def send_message_telegram_update_gain_balance(balance):
    message = '** With the latest operation ,the current balance is {}$ **'.format(balance)
    requests.post(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                               message))


def send_message_telegram_set_stop_loss(symbol, sl):
    message = '** Stop Loss successfully placed to Initial Price for Pair {} with value {} for free ride {} **'.format(
        symbol, sl, '\N{grimacing face}')
    requests.post(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                               message))


def send_daily_report(listBroker, strategy):
    for account in listBroker:
        message = daily_report(account, strategy)
        requests.post(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                                   message))


def send_message_close_order(closeOrders):
    for order in closeOrders:
        if order['profit'] > 0:
            message = '** Close Trade **\nSymbol: {}\nProfit: {}$\n{}'.format(order['symbol'], order['profit'],
                                                                              '\N{money-mouth face}')
        elif order['profit'] < 0:
            message = '** Close Trade **\nSymbol: {}\nLoss: {}$\n{}'.format(order['symbol'], order['profit'],
                                                                            '\N{loudly crying face}')
        requests.post(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                                   message))
        closeOrders.remove(order)
        account_info_dict = mt5.account_info()._asdict()
        balance = account_info_dict['balance']
        send_message_telegram_update_gain_balance(balance)


def send_scalping_scalping(profit):
    if profit > 0:
        message = "** Close all Scalping positions **\nProfit :{}$\n{}".format(round(profit, 2), '\N{money-mouth face}')
        requests.post(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                                   message))


def send_manual_profit(profit):
    if profit > 0:
        message = "** Close all Manual position **\nProfit :{}$\n{}".format(round(profit, 2), '\N{money-mouth face}')
        requests.post(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                                   message))
    elif profit < 0:
        message = "** Close all Manual position **\nProfit :{}$\n{}".format(round(profit, 2),
                                                                              '\N{loudly crying face}')
        requests.post(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                                   message))

