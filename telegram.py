TOKEN = '5001454581:AAGXNd0w_kwgXGZsvHozjs8ROh8Ijjlchqc'
CHAT_ID = "402059449"

import requests


def send_message_telegram_open_trade(symbol, lot):
    message = 'Open Trade for {} with lot {}'.format(symbol, lot)
    requests.post('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, CHAT_ID, message))


def send_message_telegram_close_trade(symbol, profit):
    message = 'Close Trade for {} with profit {}'.format(symbol, profit)
    requests.post('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(TOKEN, CHAT_ID, message))


send_message_telegram_open_trade("XAUUSD",0.25)