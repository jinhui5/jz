from telegram.ext import CommandHandler, MessageHandler, filters
from .commands import set_operator, remove_operator, show_operators

def setup_handlers(application):
    # 注册 /set_operator 命令
    application.add_handler(CommandHandler("set_operator", set_operator))
    
    # 注册 /remove_operator 命令
    application.add_handler(CommandHandler("remove_operator", remove_operator))

    # 注册 /show_operators 命令
    application.add_handler(CommandHandler("show_operators", show_operators))
    
    # 注册 "设置操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'设置操作人'), set_operator))

    # 注册 "删除操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'删除操作人'), remove_operator))

    # 注册 "设置操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'设置操作人'), set_operator))
