#!/usr/bin/with-contenv bashio

export 8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM=$(bashio::config 'bot_token')

exec python3 /app/prod_report_bot.py
