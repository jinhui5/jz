import requests
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
    operators_list = "\n".join([f"{row[0]}" for row in result])

    # 发送操作人列表
    await update.message.reply_text(f"当前操作人列表:\n{operators_list}")

    conn.close()

# 显示实时汇率的异步函数
async def show_exchange_rate(update: Update, context: CallbackContext) -> None:
    # CoinGecko API URL
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=cny"
    
    # 获取汇率数据
    try:
        response = requests.get(url)
        data = response.json()

        # 检查 API 返回的数据
        if "tether" not in data or "cny" not in data["tether"]:
            await update.message.reply_text("无法获取汇率数据，请稍后再试。")
            return

        # 获取 USDT 对 CNY 的汇率
        exchange_rate = data["tether"]["cny"]

        # 返回汇率结果
        await update.message.reply_text(f"当前 USDT 对 CNY 的实时汇率是: {exchange_rate} CNY")
    
    except Exception as e:
        await update.message.reply_text("获取汇率时发生错误，请稍后再试。")
        print(f"Error: {e}")

# 获取实时汇率并计算金额的异步函数
async def set_exchange_rate(update: Update, context: CallbackContext) -> None:
    # 获取用户输入的金额
    try:
        amount = float(context.args[0])  # 获取用户输入的金额
    except (IndexError, ValueError):
        await update.message.reply_text("请提供有效的金额，例如: `/set_exchange_rate 100`")
        return

    # CoinGecko API URL
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=cny"
    
    # 获取汇率数据
    try:
        response = requests.get(url)
        data = response.json()

        # 检查 API 返回的数据
        if "tether" not in data or "cny" not in data["tether"]:
            await update.message.reply_text("无法获取汇率数据，请稍后再试。")
            return

        # 获取 USDT 对 CNY 的汇率
        exchange_rate = data["tether"]["cny"]

        # 计算兑换金额
        converted_amount = amount * exchange_rate

        # 返回计算结果
        await update.message.reply_text(f"当前 USDT 对 CNY 的实时汇率是: {exchange_rate} CNY\n"
                                       f"{amount} USDT = {converted_amount} CNY")
    
    except Exception as e:
        await update.message.reply_text("获取汇率时发生错误，请稍后再试。")
        print(f"Error: {e}")

# 入款人民币的异步函数
async def deposit_rmb(update: Update, context: CallbackContext) -> None:
    # 获取用户输入的文本
    text = update.message.text.strip()

    # 确保输入格式是 +数字c
    if not text.startswith('+') or not text.endswith('c'):
        await update.message.reply_text("请输入有效的入款命令，例如: `+100c`。")
        return

    # 提取金额（去掉 '+' 和 'c'）
    try:
        amount = float(text[1:-1])  # 提取金额并转换为浮动类型
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `+100c`。")
        return

    # 将入款金额存入数据库（假设每个用户都有唯一的 ID）
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # 插入入款记录
    cursor.execute("INSERT INTO deposits (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    conn.commit()

    # 反馈给用户
    await update.message.reply_text(f"成功入款 {amount} 人民币！")

    conn.close()

# 支出人民币的异步函数
async def spend_rmb(update: Update, context: CallbackContext) -> None:
    # 获取用户输入的文本
    text = update.message.text.strip()

    # 确保输入格式是 -数字c
    if not text.startswith('-') or not text.endswith('c'):
        await update.message.reply_text("请输入有效的支出命令，例如: `-100c`。")
        return

    # 提取金额（去掉 '-' 和 'c'）
    try:
        amount = float(text[1:-1])  # 提取金额并转换为浮动类型
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `-100c`。")
        return

    # 将支出金额存入数据库（假设每个用户都有唯一的 ID）
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # 插入支出记录
    cursor.execute("INSERT INTO expenses (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    conn.commit()

    # 反馈给用户
    await update.message.reply_text(f"成功支出 {amount} 人民币！")

    conn.close()

# 入款 USDT 的异步函数
async def deposit_usdt(update: Update, context: CallbackContext) -> None:
    # 获取用户输入的文本
    text = update.message.text.strip()

    # 确保输入格式是 +数字u
    if not text.startswith('+') or not text.endswith('u'):
        await update.message.reply_text("请输入有效的入款命令，例如: `+100u`。")
        return

    # 提取金额（去掉 '+' 和 'u'）
    try:
        amount = float(text[1:-1])  # 提取金额并转换为浮动类型
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `+100u`。")
        return

    # 将入款金额存入数据库（假设每个用户都有唯一的 ID）
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # 插入入款记录
    cursor.execute("INSERT INTO usdt_deposits (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    conn.commit()

    # 反馈给用户
    await update.message.reply_text(f"成功入款 {amount} USDT！")

    conn.close()

# 支出 USDT 的异步函数
async def spend_usdt(update: Update, context: CallbackContext) -> None:
    # 获取用户输入的文本
    text = update.message.text.strip()

    # 确保输入格式是 -数字u
    if not text.startswith('-') or not text.endswith('u'):
        await update.message.reply_text("请输入有效的支出命令，例如: `-100u`。")
        return

    # 提取金额（去掉 '-' 和 'u'）
    try:
        amount = float(text[1:-1])  # 提取金额并转换为浮动类型
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `-100u`。")
        return

    # 将支出金额存入数据库（假设每个用户都有唯一的 ID）
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    # 插入支出记录
    cursor.execute("INSERT INTO usdt_expenses (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    conn.commit()

    # 反馈给用户
    await update.message.reply_text(f"成功支出 {amount} USDT！")

    conn.close()
