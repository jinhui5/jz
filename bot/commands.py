from telegram import Update
from telegram.ext import CallbackContext
from .db import get_db_connection

def set_operator(update: Update, context: CallbackContext) -> None:
    # 设置操作员的代码
    ...

def add_ledger(update: Update, context: CallbackContext) -> None:
    # 记账的代码
    ...

def get_ledger(update: Update, context: CallbackContext) -> None:
    # 获取记账记录的代码
    ...

