from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import re
import logging

TOKEN = "8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM"
user_stats = {}

logging.basicConfig(level=logging.INFO)

def parse_report(text):
    try:
        result = {
            "Паков": 0,
            "Вес": 0,
            "Пакетосварка": 0,
            "Флекса": 0,
            "Экструзия_м": 0,
            "Экструзия_т": 0,
            "Итого": 0
        }
        lines = text.splitlines()
        for line in lines:
            line = line.strip().lower()
            if line.startswith("паков"):
                result["Паков"] = int(re.findall(r"\d+", line)[0])
            elif line.startswith("вес"):
                result["Вес"] = int(re.findall(r"\d+", line)[0])
            elif "пакетосварка" in line:
                result["Пакетосварка"] = int(re.findall(r"\d+", line)[0])
            elif "флекс" in line:
                result["Флекса"] = int(re.findall(r"\d+", line)[0])
            elif "экструзия" in line:
                m = re.search(r"м(\d+)", line)
                t = re.search(r"т(\d+)", line)
                if m: result["Экструзия_м"] = int(m.group(1))
                if t: result["Экструзия_т"] = int(t.group(1))
            elif line.startswith("итого"):
                result["Итого"] = int(re.findall(r"\d+", line)[0])
        return result
    except Exception as e:
        return None

async def start(update, context):
    await update.message.reply_text("Привет! Пришли мне сменный отчёт.")

async def stats(update, context):
    user = update.effective_user.first_name
    if user in user_stats:
        stats = user_stats[user]
        reply = f"📊 Статистика для {user}:\n"
        for k, v in stats.items():
            reply += f"{k}: {v}\n"
    else:
        reply = "Нет сохранённых данных."
    await update.message.reply_text(reply)

async def handle_message(update, context):
    user = update.effective_user.first_name
    parsed = parse_report(update.message.text)
    if not parsed:
        await update.message.reply_text("Не удалось распознать отчёт.")
        return
    if user not in user_stats:
        user_stats[user] = {k: 0 for k in parsed}
    for k in parsed:
        user_stats[user][k] += parsed[k]
    reply = (
        f"✅ Принято от {user}:\n"
        f"📦 Паков: {parsed['Паков']}\n"
        f"⚖️ Вес: {parsed['Вес']}\n"
        f"♻️ Отходы:\n"
        f"  🧵 Пакетосварка: {parsed['Пакетосварка']}\n"
        f"  🎨 Флекса: {parsed['Флекса']}\n"
        f"  🏭 Экструзия: м{parsed['Экструзия_м']} т{parsed['Экструзия_т']}\n"
        f"♻️ Итого отходов: {parsed['Итого']}"
    )
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
