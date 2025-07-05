from telegram.ext import CommandHandler, MessageHandler, filters  
from .commands import set_operator

def setup_handlers(application):
    # 注册 /set_operator 命令
    application.add_handler(CommandHandler("set_operator", set_operator))

    # 使用 filters.Text 和 filters.Regex 来组合过滤条件
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'设置操作人'), set_operator))
