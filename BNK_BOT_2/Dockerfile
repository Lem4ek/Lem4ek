FROM python:3.12-slim

WORKDIR /app
COPY prod_report_bot.py .

RUN pip install python-telegram-bot==20.8

CMD ["python", "prod_report_bot.py"]
