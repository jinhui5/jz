from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from .commands import start_set_operator, set_operator

def setup_handlers(application):
    # 使用 ConversationHandler 来处理交互式对话
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text & filters.Regex(r'设置操作人'), start_set_operator)],
        states={
            # 用户输入用户名的状态
            1: [MessageHandler(filters.Text & ~filters.Command(), set_operator)],
        },
        fallbacks=[],
    )

    # 注册处理器
    application.add_handler(conv_handler)
