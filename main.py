from flask import *
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from checkptofittarget import close_all_trade_with_profit
from cleanloss import close_order_limit_loss
from mt5 import *
from scalping import scalping_strategy
from takeprofit import update_position_take_profit
from pipsstrategy import close_order_15_pips

brokerFXDD50k = {
    "login": 826838,
    "server": "BRKHoldings-Demo",
    "password": "mv7fjeql",
    "comment": "Long Run",
    "lot": 2
}

listBroker = []
listBroker.append(brokerFXDD50k)


def run_schedule_take_profit():
    update_position_take_profit(listBroker)


def run_schedule_close_order():
    close_order_limit_loss(listBroker)


def close_all_profit():
    close_all_trade_with_profit(listBroker)


def fifteen_pips():
    close_order_15_pips(brokerFXDD50k)


sched = BackgroundScheduler(daemon=True)
# sched.add_job(run_schedule_take_profit, trigger='cron', minute='*/5')
sched.add_job(run_schedule_close_order, trigger='cron', second='*/1')
# sched.add_job(close_all_profit,trigger='cron', minute='10,20,40,50')
# sched.add_job(fifteen_pips, trigger='cron',minute='2-4,6-9,11-14,16-19,21-24,26-29,31-34,36-39,41-44,46-49,51-54,56-59')
sched.start()

app = Flask(__name__)


@app.route("/tradingview", methods=['GET', 'POST'])
def home():
    json_data = request.json
    symbol = str(json_data["symbol"])
    order = str(json_data["order"]).upper()

    message = symbol + " - " + order
    print("***PLACING ORDER***")
    print(message)

    if symbol == "GER30":
        symbol = "GER.30"
    elif symbol == "US100":
        symbol = "NAS100"
    elif symbol == "US500":
        symbol = "SPX500"
    elif symbol == "ETHUSDT":
        symbol = "ETHUSD"
    elif symbol == "BTCUSDT":
        symbol = "BTCUSD"
    elif symbol == "USOIL":
        symbol = "OILUSD"

    open_trade(order, symbol, listBroker)

    print("***     END     ***")
    return message


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
