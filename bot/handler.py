from telegram.ext import CommandHandler, MessageHandler, filters
from .commands import set_operator, remove_operator, show_operators, show_exchange_rate, set_exchange_rate, deposit_rmb, spend_rmb, deposit_usdt

def setup_handlers(application):
    # 注册 /set_operator 命令
    application.add_handler(CommandHandler("set_operator", set_operator))
    
    # 注册 /remove_operator 命令
    application.add_handler(CommandHandler("remove_operator", remove_operator))

    # 注册 /show_operators 命令
    application.add_handler(CommandHandler("show_operators", show_operators))

    # 注册 /show_exchange_rate 命令
    application.add_handler(CommandHandler("show_exchange_rate", show_exchange_rate))

    # 注册 /set_exchange_rate 命令
    application.add_handler(CommandHandler("set_exchange_rate", set_exchange_rate))

    # 注册 "入款人民币" 命令 (+数字c)
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\+\d+\.?\d*c$'), deposit_rmb))

    # 注册 /spend_rmb 命令 (-数字c)
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\-\d+\.?\d*c$'), spend_rmb))

    # 注册 /deposit_usdt 命令 (+数字u)
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\+\d+\.?\d*u$'), deposit_usdt))
    
    # 注册 "设置操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'设置操作人'), set_operator))

    # 注册 "删除操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'删除操作人'), remove_operator))

    # 注册 "显示操作人" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'显示操作人'), show_operators))

    # 注册 "显示实时汇率" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'显示实时汇率'), show_exchange_rate))

    # 注册 "设置实时汇率" 文本输入
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'设置实时汇率'), set_exchange_rate))

