from telegram import Update
from telegram.ext import CallbackContext
from .db import get_db_connection

# 设置操作员的异步函数
async def set_operator(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # 获取用户输入的文本
    text = update.message.text.strip()

    # 检查用户输入是否包含目标用户名
    if len(text.split()) < 2:
        await update.message.reply_text("请提供要设置的操作人用户名，例如: `/set_operator @username` 或直接输入用户名。")
        return

    target_username = text.split()[1]  # 提取目标用户名

    # 使用 await 获取群管理员列表
    admins = await update.message.chat.get_administrators()

    # 检查用户是否是群主或管理员
    if not any(admin.user.id == user_id for admin in admins):
        await update.message.reply_text("只有群主或管理员可以设置操作人！")
        return

    # 获取用户 ID
    target_user_id = None
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查找目标用户的 ID
    cursor.execute("SELECT user_id FROM operators WHERE username = %s", (target_username,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"用户 {target_username} 已经是操作人！")
        return

    # 查找目标用户的 ID
    target_user_id = None
    for admin in admins:
        if admin.user.username == target_username.lstrip('@'):
            target_user_id = admin.user.id
            break

    if target_user_id is None:
        await update.message.reply_text(f"没有找到用户 {target_username}。请检查用户名是否正确。")
        return

    # 将该用户设置为操作人
    cursor.execute("INSERT INTO operators (user_id, username, is_admin) VALUES (%s, %s, %s)", 
                   (target_user_id, target_username, False))
    conn.commit()
    await update.message.reply_text(f"已将 {target_username} 设置为操作人！")

    conn.close()

# 删除操作员的异步函数
async def remove_operator(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # 使用 await 获取群管理员列表
    admins = await update.message.chat.get_administrators()

    # 检查用户是否是群主或管理员
    if not any(admin.user.id == user_id for admin in admins):
        await update.message.reply_text("只有群主或管理员可以删除操作人！")
        return

    # 获取用户输入的文本
    text = update.message.text.strip()

    # 确保用户输入有效的 @username
    if len(text.split()) < 2:
        await update.message.reply_text("请提供要删除的操作人用户名，例如: `/remove_operator @username` 或直接输入用户名。")
        return

    target_username = text.split()[1]  # 提取目标用户名

    # 获取用户 ID
    target_user_id = None
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查找目标用户的 ID
    cursor.execute("SELECT user_id FROM operators WHERE username = %s", (target_username,))
    result = cursor.fetchone()

    if result is None:
        await update.message.reply_text(f"没有找到用户 {target_username} 作为操作人。")
        return

    target_user_id = result[0]

    # 从数据库中删除该用户
    cursor.execute("DELETE FROM operators WHERE user_id = %s", (target_user_id,))
    conn.commit()

    await update.message.reply_text(f"已删除 {target_username} 作为操作人！")

    conn.close()

# 显示操作人的异步函数
async def show_operators(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # 使用 await 获取群管理员列表
    admins = await update.message.chat.get_administrators()

    # 检查用户是否是群主或管理员
    if not any(admin.user.id == user_id for admin in admins):
        await update.message.reply_text("只有群主或管理员可以查看操作人！")
        return

    # 获取操作人列表
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查询所有操作人
    cursor.execute("SELECT username FROM operators")
    result = cursor.fetchall()

    if not result:
        await update.message.reply_text("当前没有设置操作人。")
        conn.close()
        return

    # 构建操作人列表
    operators_list = "\n".join([f"@{row[0]}" for row in result])

    # 发送操作人列表
    await update.message.reply_text(f"当前操作人列表:\n{operators_list}")

    conn.close()
