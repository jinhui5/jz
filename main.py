import logging
from telegram.ext import Updater
from bot.handler import setup_handlers
from bot.config import TELEGRAM_TOKEN

def main():
    # 启动日志记录
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger()

    # 设置 Updater
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # 设置命令处理器
    setup_handlers(updater.dispatcher)

    # 启动机器人
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
