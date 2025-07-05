import requests
import pytz
from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime, timedelta
from pytz import timezone
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

# 获取实时汇率的函数
def get_exchange_rate():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=cny"
    try:
        response = requests.get(url)
        data = response.json()
        if "tether" not in data or "cny" not in data["tether"]:
            return None
        return data["tether"]["cny"]
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

# 获取并显示最近的入款或支出记录（包括北京时间格式）
def get_recent_records(user_id, currency, transaction_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查询最近三条记录
    cursor.execute(f"""
        SELECT amount, transaction_date 
        FROM daily_bill
        WHERE user_id = %s AND currency = %s AND transaction_type = %s
        ORDER BY transaction_date DESC LIMIT 3
    """, (user_id, currency, transaction_type))

    records = cursor.fetchall()
    conn.close()

    return records

# 格式化交易记录
def format_records(records, currency, transaction_type):
    if not records:
        return f"没有找到最近的{currency} {transaction_type}记录。"
    
    formatted = ""
    beijing_tz = pytz.timezone("Asia/Shanghai")  # 设置北京时间时区
    for record in records:
        amount, transaction_date = record
        # 转换时间为北京时间
        transaction_date = transaction_date.astimezone(beijing_tz)
        # 格式化时间为"小时:分钟"
        time = transaction_date.strftime("%H:%M")
        formatted += f"{time} {transaction_type} {amount:.2f} {currency}\n"
    
    return formatted

# CNY入款记录通知
async def deposit_rmb(update: Update, context: CallbackContext) -> None:
    text = update.message.text.strip()
    if not text.startswith('+') or not text.endswith('c'):
        await update.message.reply_text("请输入有效的入款命令，例如: `+100c`。")
        return

    try:
        amount = float(text[1:-1])  # 提取金额
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `+100c`。")
        return

    # 获取汇率
    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        await update.message.reply_text("无法获取汇率数据，请稍后再试。")
        return

    # 计算USDT金额
    usdt_amount = amount / exchange_rate

    # 获取当前时间
    beijing_tz = pytz.timezone("Asia/Shanghai")
    current_time = datetime.now(beijing_tz).strftime("%H:%M")  # 获取当前时间（小时:分钟）

    # 存储入款记录
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO deposits (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    cursor.execute("INSERT INTO daily_bill (user_id, amount, currency, transaction_type, transaction_date) "
                   "VALUES (%s, %s, 'CNY', 'deposit', CURRENT_DATE)", (user_id, amount))
    conn.commit()

    # 获取最近三条入款记录
    recent_records = get_recent_records(user_id, 'CNY', 'deposit')
    formatted_records = format_records(recent_records, 'CNY', '入款')

    # 发送通知消息
    await update.message.reply_text(f"{current_time} +{amount} CNY / {exchange_rate:.2f} = +{usdt_amount:.2f} USDT\n\n最近三条入款记录：\n{formatted_records}")

    conn.close()

# CNY支出记录通知
async def spend_rmb(update: Update, context: CallbackContext) -> None:
    text = update.message.text.strip()
    if not text.startswith('-') or not text.endswith('c'):
        await update.message.reply_text("请输入有效的支出命令，例如: `-100c`。")
        return

    try:
        amount = float(text[1:-1])  # 提取金额
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `-100c`。")
        return

    # 获取汇率
    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        await update.message.reply_text("无法获取汇率数据，请稍后再试。")
        return

    # 计算USDT金额
    usdt_amount = amount / exchange_rate

    # 获取当前时间
    beijing_tz = pytz.timezone("Asia/Shanghai")
    current_time = datetime.now(beijing_tz).strftime("%H:%M")  # 获取当前时间（小时:分钟）

    # 存储支出记录
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    cursor.execute("INSERT INTO daily_bill (user_id, amount, currency, transaction_type, transaction_date) "
                   "VALUES (%s, %s, 'CNY', 'spend', CURRENT_DATE)", (user_id, amount))
    conn.commit()

    # 获取最近三条支出记录
    recent_records = get_recent_records(user_id, 'CNY', 'spend')
    formatted_records = format_records(recent_records, 'CNY', '支出')

    # 发送通知消息
    await update.message.reply_text(f"{current_time} -{amount} CNY / {exchange_rate:.2f} = -{usdt_amount:.2f} USDT\n\n最近三条支出记录：\n{formatted_records}")

    conn.close()

# USDT入款记录通知
async def deposit_usdt(update: Update, context: CallbackContext) -> None:
    text = update.message.text.strip()
    if not text.startswith('+') or not text.endswith('u'):
        await update.message.reply_text("请输入有效的入款命令，例如: `+100u`。")
        return

    try:
        amount = float(text[1:-1])  # 提取金额
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `+100u`。")
        return

    # 获取汇率
    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        await update.message.reply_text("无法获取汇率数据，请稍后再试。")
        return

    # 计算CNY金额
    cny_amount = amount * exchange_rate

    # 获取当前时间
    beijing_tz = pytz.timezone("Asia/Shanghai")
    current_time = datetime.now(beijing_tz).strftime("%H:%M")  # 获取当前时间（小时:分钟）

    # 存储入款记录
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usdt_deposits (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    cursor.execute("INSERT INTO daily_bill (user_id, amount, currency, transaction_type, transaction_date) "
                   "VALUES (%s, %s, 'USDT', 'deposit', CURRENT_DATE)", (user_id, amount))
    conn.commit()

    # 获取最近三条入款记录
    recent_records = get_recent_records(user_id, 'USDT', 'deposit')
    formatted_records = format_records(recent_records, 'USDT', '入款')

    # 发送通知消息
    await update.message.reply_text(f"{current_time} +{amount} USDT * {exchange_rate:.2f} = +{cny_amount:.2f} CNY\n\n最近三条入款记录：\n{formatted_records}")

    conn.close()

# USDT支出记录通知
async def spend_usdt(update: Update, context: CallbackContext) -> None:
    text = update.message.text.strip()
    if not text.startswith('-') or not text.endswith('u'):
        await update.message.reply_text("请输入有效的支出命令，例如: `-100u`。")
        return

    try:
        amount = float(text[1:-1])  # 提取金额
    except ValueError:
        await update.message.reply_text("请输入有效的金额，例如: `-100u`。")
        return

    # 获取汇率
    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        await update.message.reply_text("无法获取汇率数据，请稍后再试。")
        return

    # 计算CNY金额
    cny_amount = amount * exchange_rate

    # 获取当前时间
    beijing_tz = pytz.timezone("Asia/Shanghai")
    current_time = datetime.now(beijing_tz).strftime("%H:%M")  # 获取当前时间（小时:分钟）

    # 存储支出记录
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usdt_expenses (user_id, amount) VALUES (%s, %s)", (user_id, amount))
    cursor.execute("INSERT INTO daily_bill (user_id, amount, currency, transaction_type, transaction_date) "
                   "VALUES (%s, %s, 'USDT', 'spend', CURRENT_DATE)", (user_id, amount))
    conn.commit()

    # 获取最近三条支出记录
    recent_records = get_recent_records(user_id, 'USDT', 'spend')
    formatted_records = format_records(recent_records, 'USDT', '支出')

    # 发送通知消息
    await update.message.reply_text(f"{current_time} -{amount} USDT * {exchange_rate:.2f} = -{cny_amount:.2f} CNY\n\n最近三条支出记录：\n{formatted_records}")

    conn.close()

# 获取并显示今日账单的异步函数
async def show_daily_bill(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # 设置时区为北京时间
    beijing_tz = timezone("Asia/Shanghai")
    today = datetime.now(beijing_tz).date()  # 获取北京时间的今天日期

    # 格式化日期为 "YYYY-MM-DD"
    formatted_date = today.strftime("%Y-%m-%d")

    # 从数据库中获取今天的入款和支出数据
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取今日 CNY 入款
    cursor.execute("SELECT SUM(amount) FROM daily_bill WHERE currency = 'CNY' AND transaction_type = 'deposit' AND transaction_date = %s", (today,))
    cny_deposit = cursor.fetchone()[0] or 0

    # 获取今日 CNY 支出
    cursor.execute("SELECT SUM(amount) FROM daily_bill WHERE currency = 'CNY' AND transaction_type = 'spend' AND transaction_date = %s", (today,))
    cny_spend = cursor.fetchone()[0] or 0

    # 获取今日 USDT 入款
    cursor.execute("SELECT SUM(amount) FROM daily_bill WHERE currency = 'USDT' AND transaction_type = 'deposit' AND transaction_date = %s", (today,))
    usdt_deposit = cursor.fetchone()[0] or 0

    # 获取今日 USDT 支出
    cursor.execute("SELECT SUM(amount) FROM daily_bill WHERE currency = 'USDT' AND transaction_type = 'spend' AND transaction_date = %s", (today,))
    usdt_spend = cursor.fetchone()[0] or 0

    # 计算总入款和支出
    total_cny_deposit = cny_deposit
    total_cny_spend = cny_spend
    total_usdt_deposit = usdt_deposit
    total_usdt_spend = usdt_spend

    # 构建账单信息，使用 Markdown 格式
    bill_message = f"*今日账单（北京时间） - {formatted_date}:*\n\n"
    
    # CNY 入款和支出
    bill_message += f"CNY 入款: `{total_cny_deposit:.2f} CNY`\n"
    bill_message += f"CNY 支出: `-{total_cny_spend:.2f} CNY`\n"
    bill_message += f"CNY 总余额: `{total_cny_deposit - total_cny_spend:.2f} CNY`\n\n"

    # USDT 入款和支出
    bill_message += f"USDT 入款: `{total_usdt_deposit:.2f} USDT`\n"
    bill_message += f"USDT 支出: `-{total_usdt_spend:.2f} USDT`\n"
    bill_message += f"USDT 总余额: `{total_usdt_deposit - total_usdt_spend:.2f} USDT`\n"

    # 添加自定义文字和链接
    bill_message += "\n\n*本机器人完全免费使用！*\n"
    bill_message += " [Ant科技官方频道](https://t.me/antkeji)\n"

    # 发送账单信息
    await update.message.reply_text(bill_message, parse_mode="Markdown")

    conn.close()

# 删除今日账单的异步函数
async def delete_daily_bill(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # 获取当前日期（北京时间）
    beijing_tz = timezone("Asia/Shanghai")
    today = datetime.now(beijing_tz).date()  # 获取北京时间的今天日期

    # 使用 await 获取群管理员列表
    admins = await update.message.chat.get_administrators()

    # 检查用户是否是群主或管理员
    if not any(admin.user.id == user_id for admin in admins):
        await update.message.reply_text("只有群主或管理员可以删除账单！")
        return

    # 从数据库中删除今日账单记录
    conn = get_db_connection()
    cursor = conn.cursor()

    # 删除今天的 CNY 入款、支出记录
    cursor.execute("DELETE FROM daily_bill WHERE transaction_date = %s", (today,))

    # 提交删除操作
    conn.commit()

    # 反馈给用户
    await update.message.reply_text(f"成功删除了 {today} 的账单！")

    conn.close()
