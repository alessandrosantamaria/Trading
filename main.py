from flask import *
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from cleanloss import close_order_limit_loss
from mt5 import *
from scalping import scalping_strategy
from takeprofit import update_position_take_profit
from pipsstrategy import close_order_15_pips

brokerFXDD50k = {
    "login": 817430,
    "server": "BRKHoldings-Demo",
    "password": "wq8xzthh",
    "size": 1.0,
    "sizeZar": 0.50,
    "sizeXau": 0.50,
    "sellLimit": 400,
    "noLossLimit": 150,
    "closeOrderLimit": -200,
    "scalpingTarget":10,
    "clubEliteSize": 0.50,
    "15pips": 150
}

brokerFXDD100k = {
    "login": 817544,
    "server": "BRKHoldings-Demo",
    "password": "a6fiomsh",
    "size": 1.0,
    "sizeZar": 0.50,
    "sizeXau": 0.50,
    "sellLimit": 800,
    "noLossLimit": 400,
    "closeOrderLimit": -200,
    "scalpingTarget": 10,
    "clubEliteSize": 0.50,
    "15pips": 150
}


listBroker = []
listBroker.append(brokerFXDD50k)
listBroker.append(brokerFXDD100k)

def run_schedule_take_profit():
    update_position_take_profit(brokerFXDD50k)

def run_schedule_close_order():
    close_order_limit_loss(listBroker)

def scalping():
    scalping_strategy(listBroker)

def fifteen_pips():
    close_order_15_pips(brokerFXDD100k)

sched = BackgroundScheduler(daemon=True)
sched.add_job(run_schedule_take_profit,trigger='cron', minute='*/5')
#sched.add_job(run_schedule_close_order,trigger='cron', minute='1,16,36,46')
#sched.add_job(scalping,trigger='cron', minute='3-29,35-59')
sched.add_job(fifteen_pips,trigger='cron', minute='2-4,6-9,11-14,16-19,21-24,26-29,31-34,36-39,41-44,46-49,51-54,56-59')
sched.start()








app = Flask(__name__)


@app.route("/tradingview", methods=['GET', 'POST'])
def home():
    json_data = request.json
    symbol = str(json_data["symbol"])
    order = str(json_data["order"])
    message = symbol + " - " + order
    print("***PLACING ORDER***")
    print(message)
    open_trade(order, symbol,listBroker)
    print("***     END     ***")
    return message


if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)

