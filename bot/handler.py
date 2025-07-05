from telegram.ext import CommandHandler, MessageHandler, filters
from .commands import set_operator

def setup_handlers(application):
    # 注册处理 "设置操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'设置操作人'), set_operator))
