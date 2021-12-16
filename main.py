from flask import *
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from close_all_positions import close_all_trade_with_profit
from check_position_gain import close_order_limit_loss
from constraints import *
from mt5_open_close_orders import *
from set_stop_loss import update_position_take_profit

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


sched = BackgroundScheduler(daemon=True)
# sched.add_job(run_schedule_take_profit, trigger='cron', minute='*/5')
sched.add_job(run_schedule_close_order, trigger='cron', second='*/1')
# sched.add_job(close_all_profit,trigger='cron', minute='10,20,40,50')
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
        symbol = DAX_MT5
    elif symbol == "US100":
        symbol = NASDAQ_MT5
    elif symbol == "US500":
        symbol = SP500_MT5
    elif symbol == "ETHUSDT":
        symbol = ETH_MT5
    elif symbol == "BTCUSDT":
        symbol = BTC_MT5

    open_trade(order, symbol, listBroker)

    print("***     END     ***")
    return message


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
