from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import re
import os
import json
from datetime import datetime
import pandas as pd

BOT_TOKEN = "8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM"
HISTORY_FILE = "report_full_history.json"
EXCEL_FILE = "report_log.xlsx"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def parse_report(text):
    result = {}
    lines = text.strip().splitlines()
    for line in lines:
        if 'Остаток' in line:
            break
        match = re.match(r"^(\d+)[\s\-:]+(\d+)$", line.strip())
        if match:
            key, value = match.groups()
            result[int(key)] = int(value)
    return result

def append_to_excel(chat_id, report, timestamp, user):
    row = {
        "chat_id": chat_id,
        "timestamp": timestamp,
        "user": user
    }
    row.update({str(k): v for k, v in report.items()})
    df_new = pd.DataFrame([row])
    if os.path.exists(EXCEL_FILE):
        df_existing = pd.read_excel(EXCEL_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_excel(EXCEL_FILE, index=False)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.first_name or f"ID:{user_id}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = update.message.text
    report = parse_report(text)
    if not report:
        await update.message.reply_text("Отчёт не распознан.")
        return
    history = load_history()
    reports = history.get(chat_id, [])
    reports.append(report)
    history[chat_id] = reports
    save_history(history)
    append_to_excel(chat_id, report, timestamp, username)
    total = sum(report.values())
    reply = "\n".join([f"{k} - {v}" for k, v in report.items()] + [f"Итого: {total}"])
    await update.message.reply_text(reply)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
