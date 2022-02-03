from flask import *

from apscheduler.schedulers.background import BackgroundScheduler

from check_position_gain import retrieve_position_ids, check_positionIds_close_orders, \
    check_position_gain_scalping, check_position_gain_stock

from mt5_open_close_orders import *
from set_stop_loss import update_position_stop_loss, close_orders_after_target

ids = []
close_orders = []


def run_schedule_stop_loss():
    update_position_stop_loss(listBroker)


def run_schedule_check_gain_stock():
    check_position_gain_stock(listBroker)


def run_schedule_check_gain():
    check_position_gain_scalping(listBroker)


def run_schedule_all_profit_target():
    close_orders_after_target(listBroker)


def run_daily_report_follow():
    send_daily_report(listBroker,LONG_STRATEGY)


def run_daily_report_manual():
    send_daily_report(listBroker,SHORT_STRATEGY)

def run_daily_report_fast():
    send_daily_report(listBroker,SCALPING_STRATEGY)

def run_telegram_close_order(close_orders=close_orders, ids=ids):
    ids = retrieve_position_ids(listBroker, ids)
    close_orders, ids = check_positionIds_close_orders(listBroker, ids, close_orders)
    send_message_close_order(close_orders)


sched = BackgroundScheduler(daemon=True, job_defaults={'max_instances': 4})
sched.add_job(run_schedule_stop_loss, trigger='cron', second='*/10', misfire_grace_time=5)
sched.add_job(run_schedule_all_profit_target, trigger='cron', second='*/10', misfire_grace_time=5)
#sched.add_job(run_schedule_check_gain, trigger='cron', second='*/5', misfire_grace_time=5)
sched.add_job(run_schedule_check_gain_stock, trigger='cron', second='*/6', misfire_grace_time=5)
# sched.add_job(run_daily_report_follow,trigger='cron', day='*/1')
sched.add_job(run_daily_report_follow, trigger='cron', day='*/1')
sched.add_job(run_daily_report_manual, trigger='cron', day='*/1')
sched.add_job(run_daily_report_fast, trigger='cron', day='*/1')
sched.add_job(run_telegram_close_order, trigger='cron', second='*/2', misfire_grace_time=5)
sched.start()

app = Flask(__name__)


@app.route("/tradingview", methods=['GET', 'POST'])
def home():
    json_data = request.json
    symbol = str(json_data["symbol"])
    order = str(json_data["order"]).upper()
    sizeRenko = float(json_data["sizeRenko"])
    strategy = str(json_data["strategy"])

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
    elif symbol == "FRA40":
        symbol = FRA_MT5
    elif symbol == "ESP35":
        symbol = ESP_MT5
    elif symbol == "US30":
        symbol = DOW_MR5
    elif symbol == "TSLA":
        symbol = TESLA_MT5
    elif symbol == "GOOG":
        symbol = GOOGLE_MT5
    elif symbol == "AMZN":
        symbol = AMAZON_MT5
    elif symbol == "AAPL":
        symbol = APPLE_MT5
    elif symbol == "NFLX":
        symbol = NETFLIX_MT5
    elif symbol == "BABA":
        symbol = ALIBABA_MT5
    elif symbol == "BAC":
        symbol = BAC_MT5
    elif symbol == "BIDU":
        symbol = BIDU_MT5
    elif symbol == "TWTR":
        symbol = TWITTER_MT5
    elif symbol == "FB":
        symbol = FB_MT5

    if strategy == LONG_STRATEGY:
        open_trade_follow(order, symbol, listBroker)
    elif strategy == SHORT_STRATEGY:
        open_trade_scalping(order, symbol, listBroker)
    elif strategy == SCALPING_STRATEGY:
        open_trade_stock(order, symbol, listBroker)


    print("***     END     ***")
    return message


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
