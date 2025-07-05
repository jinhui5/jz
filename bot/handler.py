from telegram.ext import CommandHandler
from .commands import set_operator

def setup_handlers(application):
    # 注册 set_operator 命令
    application.add_handler(CommandHandler("set_operator", set_operator))
