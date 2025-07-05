from telegram.ext import Updater, CommandHandler
from .commands import set_operator, add_ledger, get_ledger

def setup_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("set_operator", set_operator))
    dispatcher.add_handler(CommandHandler("add", add_ledger))
    dispatcher.add_handler(CommandHandler("ledger", get_ledger))

