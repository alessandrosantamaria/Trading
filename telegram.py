import requests

from constraints import *
from retrieve_history import daily_report


def send_message_telegram_open_trade(symbol, lot):
    message = '** Open Trade **\nSymbol: {}\nLot: {}\n{}'.format(symbol, lot, '\N{call me hand}')
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

def send_daily_report(listBroker):
    for account in listBroker:
         message = daily_report(account)
         requests.post(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
                                                                               message))
