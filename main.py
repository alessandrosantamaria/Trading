import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import *

from apscheduler.schedulers.background import BackgroundScheduler

import constraints
from api_call import open_trade_api
from binance_retrieve import signal_crypto_percentage, retrieve_price_crypto
from check_position_gain import *

from mt5_open_close_orders import *
from retrieve_calendar import close_all_profit_and_no_trading
from set_stop_loss import update_position_stop_loss_for_follow_strategy, close_orders_after_target_for_follow_strategy

ids = []
close_orders = []

def run_schedule_stop_loss():
    update_position_stop_loss_for_follow_strategy(listBroker)

def run_close_order_scalping():
    check_position_gain_scalping(listBroker)


def run_schedule_check_hedge_scalping():
    check_hedge_for_scalp_strategy(listBroker)


def run_schedule_check_gain():
    check_position_gain_for_scalping_strategy(listBroker)


def run_schedule_all_profit_target():
    close_orders_after_target_for_follow_strategy(listBroker)


def run_daily_report_follow():
    send_daily_report(listBroker, LONG_STRATEGY)


def run_daily_report_manual():
    send_daily_report(listBroker, SHORT_STRATEGY)


def run_daily_report_fast():
    send_daily_report(listBroker, SCALPING_STRATEGY)


def run_open_trade_with_api_1_hour():
    print('Starting check for symbols\n')
    for key, value in symbols.items():
        print("Check {}".format(value['mt4']))
        open_trade_api(symbol= value['mt4'],target = 5,bar_pips= 20,time_interval="30min",lot =1,send_message=False)
        time.sleep(10)



def run_telegram_close_order(close_orders=close_orders, ids=ids):
    ids = retrieve_position_ids(listBroker, ids)
    close_orders, ids = check_position_Ids_close_orders(listBroker, ids, close_orders)
    send_message_close_order(close_orders)


def run_schedule_retrieve_calendar():
    close_all_profit_and_no_trading(listBroker, datetime.now().date())

def run_schedule_signal_crypto():
    signal_crypto_percentage(5,'4h')

def run_schedule_signal_crypto_target_reached():
    retrieve_price_crypto('RUNE', 2.879)


sched = BackgroundScheduler(daemon=True, job_defaults={'max_instances': 4})
#sched.add_job(run_schedule_stop_loss, trigger='cron', second='*/10', misfire_grace_time=5)
#sched.add_job(run_close_order_scalping, trigger='cron', second='*/1', misfire_grace_time=5)
sched.add_job(run_open_trade_with_api_1_hour, trigger='cron', minute='*/30', misfire_grace_time=5)
sched.add_job(run_schedule_signal_crypto, trigger='cron', hour='*/4', misfire_grace_time=5)

# sched.add_job(run_schedule_check_gain, trigger='cron', second='*/5', misfire_grace_time=5)
# sched.add_job(run_schedule_check_hedge_scalping, trigger='cron', second='*/6', misfire_grace_time=5)
#sched.add_job(run_daily_report_follow, trigger='cron', day='*/1')
#sched.add_job(run_daily_report_manual, trigger='cron', day='*/1')
#sched.add_job(run_daily_report_fast, trigger='cron', day='*/1')
# sched.add_job(run_schedule_retrieve_calendar, trigger='cron', day='*/1', hour='10')
#sched.add_job(run_telegram_close_order, trigger='cron', second='*/2', misfire_grace_time=5)

sched.add_job(run_schedule_signal_crypto_target_reached, trigger='cron', minute='*/5', misfire_grace_time=5)

sched.start()

app = Flask(__name__)


@app.route("/tradingview", methods=['GET', 'POST'])
def home():

    json_data = request.json
    symbol = str(json_data["symbol"])
    order = str(json_data["order"]).upper()
    if "strategy" in json_data:
         strategy = str(json_data["strategy"])
    else:
        strategy = ""
    if "trend" in json_data:
        trend = str(json_data["trend"])
    else:
        trend = "in"
    renko = float(json_data["sizeRenko"])


    message = symbol + " - " + order
    print("***PLACING ORDER***")
    print(message)

    if symbol == "GER40":
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

    if strategy == LINE_BREAK_STRATEGY:
        open_trade_line_break(order,symbol,listBroker,strategy)
    elif strategy == SCALPING_STRATEGY or strategy == 'scalping swh' or strategy == 'takeall':
        if order == "CLOSE ALL":
            close_order_scalping(order,symbol, listBroker)
        else:
            open_trade_scalping(order,symbol,listBroker,strategy)

    elif strategy == SHORT_STRATEGY:
        open_trade_with_renko_size(order,symbol,listBroker,strategy,renko)
    else:
        open_trade(order,symbol,listBroker,LONG_STRATEGY,trend)

    print("***     END     ***")
    return message


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
