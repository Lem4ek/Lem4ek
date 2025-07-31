#!/usr/bin/with-contenv bashio

export BOT_TOKEN=$(bashio::config 'bot_token')

exec python3 /app/prod_report_bot.py
