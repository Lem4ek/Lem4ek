import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import datetime
import re

TOKEN = "8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM"
data = {}

async def start(update, context):
    await update.message.reply_text("👋 Привет! Отправь мне отчёт — я всё посчитаю!")

async def stats(update, context):
    reply = "📊 Сумма по пользователям:\n"
    for user, stats in data.items():
        reply += f"\n👤 {user}:\n"
        for key, val in stats.items():
            reply += f"  {key}: {val}\n"
    await update.message.reply_text(reply or "Нет данных.")

async def handle_message(update, context):
    text = update.message.text
    user = update.message.from_user.first_name
    parsed = parse_report(text)
    if not parsed:
        await update.message.reply_text("⚠️ Не удалось распознать отчёт.")
        return

    if user not in data:
        data[user] = {k: 0 for k in parsed}
    for k in parsed:
        data[user][k] += parsed[k]

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
        print(f"Ошибка парсинга: {e}")
        return None

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
