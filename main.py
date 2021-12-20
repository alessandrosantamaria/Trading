from flask import *
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from accounts import listBroker
from check_position_gain import check_gain
from constraints import *
from mt5_open_close_orders import *
from set_stop_loss import update_position_stop_loss, update_position_stop_loss_to_price_open


def run_schedule_stop_loss():
    update_position_stop_loss(listBroker)


def run_schedule_check_gain():
    check_gain(listBroker)

def run_daily_report():
    send_daily_report(listBroker)


sched = BackgroundScheduler(daemon=True)
#sched.add_job(run_schedule_stop_loss, trigger='cron', second='*/1')
sched.add_job(run_schedule_check_gain, trigger='cron', second='*/1')
sched.add_job(run_daily_report,trigger='cron', day='*/1')

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
