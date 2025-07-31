from telegram import Update, ChatMember, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os
import json
from datetime import datetime
import pandas as pd
from collections import defaultdict
import re

# 🔧 Настройка логов
logging.basicConfig(level=logging.INFO)

TOKEN = "8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM"

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

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type in ["group", "supergroup"]:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    return True

def parse_report(text):
    result = {}
    lines = text.strip().splitlines()
    for line in lines:
        line = line.lower()
        if "паков" in line:
            result["Паков"] = int(re.findall(r"\d+", line)[-1])
        elif "вес" in line:
            result["Вес"] = int(re.findall(r"\d+", line)[-1])
        elif "пакетосварка" in line:
            result["Пакетосварка"] = int(re.findall(r"\d+", line)[-1])
        elif "флексо" in line or "флекса" in line or "флексография" in line:
            result["Флекса"] = int(re.findall(r"\d+", line)[-1])
        elif "экструзия" in line:
            числа = list(map(int, re.findall(r"\d+", line)))
            result["Экструзия"] = sum(числа)
        elif "итого" in line:
            result["Итого"] = int(re.findall(r"\d+", line)[-1])
    return result

def aggregate_reports(reports):
    total = defaultdict(int)
    for rep in reports:
        for k, v in rep.items():
            total[k] += v
    return total

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = str(update.effective_chat.id)
    user = update.effective_user.username or update.effective_user.first_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = parse_report(text)
    if not report:
        return

    history = load_history()
    history.setdefault(chat_id, [])
    history[chat_id].append(report)
    save_history(history)

    row = {"user": user, "timestamp": timestamp, **report}
    df_new = pd.DataFrame([row])
    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_excel(EXCEL_FILE, index=False)

    total = aggregate_reports(history[chat_id])
    msg = "\n".join(f"{k}: {v}" for k, v in total.items())
    await update.message.reply_text(f"Общий отчёт:\n{msg}")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("⛔ Только админ может сбросить данные.")
    chat_id = str(update.effective_chat.id)
    history = load_history()
    history[chat_id] = []
    save_history(history)
    await update.message.reply_text("✅ История сброшена.")

async def excel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(EXCEL_FILE):
        await update.message.reply_document(document=InputFile(EXCEL_FILE))
    else:
        await update.message.reply_text("Файл Excel ещё не создан.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handle_
