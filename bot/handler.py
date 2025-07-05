from telegram.ext import CommandHandler
from .commands import set_operator, add_ledger, get_ledger

def setup_handlers(application):
    application.add_handler(CommandHandler("set_operator", set_operator))
    application.add_handler(CommandHandler("add", add_ledger))
    application.add_handler(CommandHandler("ledger", get_ledger))
