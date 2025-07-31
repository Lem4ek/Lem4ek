FROM python:3.11-slim

RUN pip install python-telegram-bot==20.3 pandas openpyxl requests

COPY run.sh /run.sh
COPY bot.py /bot.py

CMD [ "/run.sh" ]
