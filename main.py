from flask import *
import requests

from mt5 import *

app = Flask(__name__)


@app.route("/tradingview", methods=['GET', 'POST'])
def home():
    json_data = request.json
    symbol = str(json_data["symbol"])
    order = str(json_data["order"])
    message = symbol + " Cross " + order

    print(message)
    open_trade(order, symbol, 0.5)
    return message


if __name__ == "__main__":
    app.run(debug=True)
