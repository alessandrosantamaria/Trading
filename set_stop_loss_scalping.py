import constraints
from accounts import listBroker
from set_stop_loss import set_stop_loss_manual_execution

symbol = constraints.CADJPY

set_stop_loss_manual_execution(symbol, listBroker)