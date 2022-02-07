import logging

import mt5
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
from accounts import listBroker
from constraints import *
from retrieve_profits import check_position_scalping_telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def profit(update, context):
    """Send a message when the command /start is issued."""
    message = check_position_scalping_telegram(listBroker, SHORT_STRATEGY)
    update.message.reply_text(message)
    message = check_position_scalping_telegram(listBroker, LONG_STRATEGY)
    update.message.reply_text(message)
    message = check_position_scalping_telegram(listBroker, SCALPING_STRATEGY)
    update.message.reply_text(message)


def close(update, context):
    """Send a message when the command /start is issued."""
    for i in listBroker:
        strategies = [LONG_STRATEGY, SHORT_STRATEGY, SCALPING_STRATEGY]
        if not mt5.initialize(login=i["login"], server=i["server"], password=i["password"]):
            print("initialize() failed for account {} , error code =".format(i["login"]), mt5.last_error())
            quit()
        for strategy in strategies:
            openOrders = mt5.positions_get()
            profit = 0
            for order in openOrders:
                if order.comment == strategy:
                    profit = order.profit + profit
                    order_type = order.type
                    symbol = order.symbol
                    volume = order.volume

                    if order_type == mt5.ORDER_TYPE_BUY:
                        order_type = mt5.ORDER_TYPE_SELL
                        price = mt5.symbol_info_tick(symbol).bid
                    else:
                        order_type = mt5.ORDER_TYPE_BUY
                        price = mt5.symbol_info_tick(symbol).ask

                    if symbol == BTC_MT5:
                        typeFilling = mt5.ORDER_FILLING_FOK
                    else:
                        typeFilling = mt5.ORDER_FILLING_IOC

                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": float(volume),
                        "type": order_type,
                        "position": order.ticket,
                        "price": price,
                        "magic": 234000,
                        "comment": order.comment,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": typeFilling,
                    }

                    mt5.order_send(close_request)
            message = '** Close All {} Trades **\nProfit: {}$\n{}'.format(strategy, profit, '\N{money-mouth face}')
            update.message.reply_text(message)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/profit')
    update.message.reply_text('/close')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN_TELEGRAM, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("profit", profit))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
