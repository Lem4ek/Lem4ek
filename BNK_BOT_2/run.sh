#!/bin/bash
export TELEGRAM_TOKEN=$(jq -r '.telegram_token' /data/options.json)
export TELEGRAM_CHAT_ID=$(jq -r '.allowed_chat_id' /data/options.json)
export HA_URL=$(jq -r '.ha_url' /data/options.json)
export HA_TOKEN=$(jq -r '.ha_token' /data/options.json)

python3 /bot.py
