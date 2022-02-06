from constraints import LONG_STRATEGY, SHORT_STRATEGY, SCALPING_STRATEGY

broker = {
    "login": 212389,
    "server": "BRKHoldings-Demo",
    "password": "alessandro123",
    "lot": 1.0,
    "stopLossPercentage": 1.6,
    "strategyLong": LONG_STRATEGY,
    "strategyShort": SHORT_STRATEGY,
    "strategyScalping": SCALPING_STRATEGY,
    "strategyManual": "xmanual"
}

listBroker = [broker]
