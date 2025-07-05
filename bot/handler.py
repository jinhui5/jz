from telegram.ext import CommandHandler, MessageHandler, Filters
from .commands import set_operator

def setup_handlers(application):
    # 注册 /set_operator 命令
    application.add_handler(CommandHandler("set_operator", set_operator))
    
    # 注册 “设置操作人” 文本输入
    application.add_handler(MessageHandler(Filters.text & Filters.regex(r'设置操作人'), set_operator))
