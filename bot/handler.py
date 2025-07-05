from telegram.ext import CommandHandler, MessageHandler, filters  # 注意这里的小写 filters
from .commands import set_operator

def setup_handlers(application):
    # 注册 /set_operator 命令
    application.add_handler(CommandHandler("set_operator", set_operator))
    
    # 注册 “设置操作人” 文本输入
    application.add_handler(MessageHandler(filters.text & filters.Regex(r'设置操作人'), set_operator))
