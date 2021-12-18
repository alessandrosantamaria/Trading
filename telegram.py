TOKEN = '5001454581:AAGXNd0w_kwgXGZsvHozjs8ROh8Ijjlchqc'
CHAT_ID = "402059449"

import requests


def send_message_telegram_open_trade(symbol, lot):
    message = 'Open Trade for {} with lot {}'.format(symbol, lot)
    requests.post('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, CHAT_ID, message))


def send_message_telegram_close_trade(symbol, profit):
    if profit > 0:
        message = '** Close Trade for {} with profit {}$ {} **'.format(symbol, profit,
                                                                       '\N{money-mouth face}')
    else:
        message = '** Close Trade for {} with loss {}$ {} **'.format(symbol, profit,
                                                                     '\N{loudly crying face}')
    requests.post('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, CHAT_ID, message))


def send_message_telegram_update_gain_balance(balance):
    message = '** With the latest operation ,the current balance is {}$ **'.format(balance)
    requests.post('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, CHAT_ID, message))
