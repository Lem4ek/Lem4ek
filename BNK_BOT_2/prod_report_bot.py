import os
import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Хранилище данных
data = []

# Парсинг строки
def parse_message(message: str) -> dict:
    result = {
        "timestamp": datetime.now(),
        "pack": None,
        "weight": None,
        "packetosvarka": None,
        "flexo": None,
        "extrusion": None,
        "total_waste": None,
    }

    lines = message.lower().splitlines()

    for line in lines:
        if "паков" in line:
            match = re.search(r"паков\s*[-–:]?\s*(\d+)", line)
            if match:
                result["pack"] = int(match.group(1))
        elif "вес" in line:
            match = re.search(r"вес\s*[-–:]?\s*(\d+)", line)
            if match:
                result["weight"] = int(match.group(1))
        elif "пакетосварка" in line:
            match = re.search(r"пакетосварка\s*[-–:]?\s*(\d+)", line)
            if match:
                result["packetosvarka"] = int(match.group(1))
        elif "флекс" in line or "флексография" in line:
            match = re.search(r"(флексография|флекса)\s*[-–:]?\s*(\d+)", line)
            if match:
                result["flexo"] = int(match.group(2))
        elif "экструзия" in line:
            match = re.findall(r"\d+", line)
            if match:
                result["extrusion"] = sum(map(int, match))
        elif "итого" in line:
            match = re.search(r"итого\s*[-–:]?\s*(\d+)", line)
            if match:
                result["total_waste"] = int(match.group(1))

    return result


# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parsed = parse_message(update.message.text)
    data.append(parsed)
    await update.message.reply_text("Данные сохранены ✅")


# Команда /reset
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global data
    data = []
    await update.message.reply_text("Данные сброшены 🔄")


# Команда /excel
async def excel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data:
        await update.message.reply_text("Нет данных для экспорта.")
        return

    df = pd.DataFrame(data)
    filename = "report.xlsx"
    df.to_excel(filename, index=False)

    with open(filename, "rb") as f:
        await update.message.reply_document(document=f)

    os.remove(filename)


# Команда /plot
async def plot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data:
        await update.message.reply_text("Нет данных для построения графика.")
        return

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    plt.figure()
    plt.plot(df["timestamp"], df["pack"], label="Паков")
    plt.plot(df["timestamp"], df["total_waste"], label="Отходы")
    plt.xlabel("Время")
    plt.ylabel("Количество")
    plt.title("Производство и отходы")
    plt.legend()
    plt.tight_layout()

    image_file = "plot.png"
    plt.savefig(image_file)
    plt.close()

    with open(image_file, "rb") as f:
        await update.message.reply_photo(f)

    os.remove(image_file)


# Главный запуск
def main():
    TOKEN = os.getenv("8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM")
    if not TOKEN:
        print("Ошибка: не задан BOT_TOKEN в переменных окружения.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("excel", excel_command))
    app.add_handler(CommandHandler("plot", plot_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
