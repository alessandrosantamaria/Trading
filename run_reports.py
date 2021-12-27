from accounts import broker
from retrieve_history import *

symbol = "XAUUSD"

listTrades = retrieve_history_by_symbol(symbol,broker)
#sum_results_trades(listTrades,symbol)
#sum_results_trades_sessions(listTrades,symbol)
sum_results_for_all_symbols(broker)
#sum_results_for_all_symbols_by_session(broker)
#historical_report(broker)