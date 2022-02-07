from constraints import LONG_STRATEGY, SHORT_STRATEGY, SCALPING_STRATEGY

broker = {
    "login": 1051110635,
    "server": "FTMO-Demo",
    "password": "B73DQ63YVK",
    "lot": 0.5,
    "stopLossPercentage": 1.6,
    "strategyLong": LONG_STRATEGY,
    "strategyShort": SHORT_STRATEGY,
    "strategyScalping": SCALPING_STRATEGY,
    "strategyManual": "xmanual"
}

listBroker = [broker]
