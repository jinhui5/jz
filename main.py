from telegram import Update
from telegram.ext import Application, CommandHandler
from bot.handler import setup_handlers
from bot.config import TELEGRAM_TOKEN

def main():
    # 启动日志记录
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger()

    # 创建 Application 实例，传入 Telegram Token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # 设置命令处理器
    setup_handlers(application)

    # 启动机器人
    application.run_polling()

if __name__ == '__main__':
    main()
