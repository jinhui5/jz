from telegram import Update
from telegram.ext import CallbackContext
from telegram import ParseMode
from .db import get_db_connection

# 设置操作员的异步函数
async def set_operator(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # 检查用户是否是群主或管理员
    if not (update.message.chat.get_member(user_id).status in ['administrator', 'creator']):
        await update.message.reply_text("只有群主或管理员可以设置操作人！")
        return

    # 检查命令是否有有效的 @username
    if len(context.args) < 1:
        await update.message.reply_text("请提供要设置的操作人用户名，例如: `/set_operator @username`")
        return

    target_username = context.args[0]  # 获取用户名
    target_user = None

    # 查找目标用户
    for member in update.message.chat.get_members():
        if member.user.username == target_username.lstrip('@'):
            target_user = member.user
            break

    if not target_user:
        await update.message.reply_text(f"没有找到用户 @{target_username}。请检查用户名是否正确。")
        return

    # 将该用户设置为操作人
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查该用户是否已经是操作员
    cursor.execute("SELECT * FROM operators WHERE user_id = %s", (target_user.id,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"用户 @{target_user.username} 已经是操作员！")
    else:
        cursor.execute("INSERT INTO operators (user_id, username, is_admin) VALUES (%s, %s, %s)", 
                       (target_user.id, target_user.username, False))
        conn.commit()
        await update.message.reply_text(f"已将 @{target_user.username} 设置为操作员！")

    conn.close()
