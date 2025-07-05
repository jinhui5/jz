from telegram import Update
from telegram.ext import CallbackContext
from .db import get_db_connection

# 设置操作员的异步函数
async def set_operator(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # 使用 await 获取群管理员列表
    admins = await update.message.chat.get_administrators()

    # 检查用户是否是群主或管理员
    if not any(admin.user.id == user_id for admin in admins):
        await update.message.reply_text("只有群主或管理员可以设置操作人！")
        return

    # 检查用户输入是否提供目标用户名
    if len(context.args) < 1:
        await update.message.reply_text("请提供要设置的操作人用户名，例如: `@username`。")
        return

    target_username = context.args[0]  # 获取用户名

    # 获取用户 ID
    target_user_id = None
    for admin in admins:
        if admin.user.username == target_username.lstrip('@'):
            target_user_id = admin.user.id
            break

    if target_user_id is None:
        await update.message.reply_text(f"没有找到用户 @{target_username}。请检查用户名是否正确。")
        return

    # 使用 get_member 获取指定用户的成员信息
    target_user = await update.message.chat.get_member(target_user_id)

    # 将该用户设置为操作人
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查该用户是否已经是操作员
    cursor.execute("SELECT * FROM operators WHERE user_id = %s", (target_user.user.id,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"用户 @{target_user.user.username} 已经是操作员！")
    else:
        cursor.execute("INSERT INTO operators (user_id, username, is_admin) VALUES (%s, %s, %s)", 
                       (target_user.user.id, target_user.user.username, False))
        conn.commit()
        await update.message.reply_text(f"已将 @{target_user.user.username} 设置为操作员！")

    conn.close()
