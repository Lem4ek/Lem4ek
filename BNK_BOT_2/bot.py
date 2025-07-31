import os
import csv
import re
import requests
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import pandas as pd

TELEGRAM_TOKEN = os.environ["8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
HA_URL = os.environ["HA_URL"]
HA_TOKEN = os.environ["HA_TOKEN"]
HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

LOG_FILE = "/data/log.csv"

FIELDNAMES = ["дата", "пользователь", "паков", "вес", "пакетосварка", "флекса", "экструзия", "итого"]

def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def parse_message(username, text):
    result = {
        "дата": datetime.now().strftime("%Y-%m-%d"),
        "пользователь": username,
        "паков": 0,
        "вес": 0,
        "пакетосварка": 0,
        "флекса": 0,
        "экструзия": "",
        "итого": 0
    }
    lines = text.lower().splitlines()
    for line in lines:
        if "паков" in line:
            result["паков"] = int(re.search(r"\d+", line).group())
        elif "вес" in line:
            result["вес"] = int(re.search(r"\d+", line).group())
        elif "пакетосварка" in line:
            result["пакетосварка"] = int(re.search(r"\d+", line).group())
        elif "флексо" in line or "флекса" in line:
            result["флекса"] = int(re.search(r"\d+", line).group())
        elif "экструзия" in line:
            result["экструзия"] = line.split("экструзия")[-1].strip()
        elif "итого" in line:
            result["итого"] = int(re.search(r"\d+", line).group())
    return result

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.chat_id) != CHAT_ID:
        return
    username = update.message.from_user.username or "unknown"
    text = update.message.text
    data = parse_message(username, text)

    ensure_log_file()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(data)

    reply = f"😊 Принято от @{username}:
"
    reply += f"📦 Паков: {data['паков']}
"
    reply += f"⚖️ Вес: {data['вес']} кг
"
    reply += f"🔧 Пакетосварка: {data['пакетосварка']}
"
    reply += f"🖨️ Флекса: {data['флекса']}
"
    reply += f"🏭 Экструзия: {data['экструзия']}
"
    reply += f"♻️ Итого отходов: {data['итого']}"

    await update.message.reply_text(reply)

async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(LOG_FILE):
        await update.message.reply_text("⛔ Нет данных.")
        return

    df = pd.read_csv(LOG_FILE)
    grouped = df.groupby("пользователь").agg({
        "паков": "sum",
        "вес": "sum",
        "итого": "sum"
    }).reset_index()

    reply = "📈 Статистика по пользователям:

"
    for _, row in grouped.iterrows():
        reply += f"👤 @{row['пользователь']}
"
        reply += f"  📦 Паков: {row['паков']}
"
        reply += f"  ⚖️ Вес: {row['вес']} кг
"
        reply += f"  ♻️ Отходы: {row['итого']} кг

"
    reply += f"🔄 Всего записей: {len(df)}"

    await update.message.reply_text(reply)

async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(LOG_FILE):
        await update.message.reply_text("⛔ Нет данных.")
        return

    df = pd.read_csv(LOG_FILE)
    excel_file = "/tmp/report.xlsx"
    df.to_excel(excel_file, index=False)

    await update.message.reply_document(InputFile(excel_file), caption="📄 Отчёт сформирован:")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CommandHandler("stats", handle_stats))
    app.add_handler(CommandHandler("report", handle_report))
    app.run_polling()

if __name__ == "__main__":
    main()
