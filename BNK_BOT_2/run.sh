#!/bin/bash
export 8199873882:AAE4x2ARLf7bR0fC9ykeOyHsrinT9JPIdRM=$(jq -r '.telegram_token' /data/options.json)
export 508532161=$(jq -r '.allowed_chat_id' /data/options.json)
export http://homeassistant.local:8123=$(jq -r '.ha_url' /data/options.json)
export eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5NDRjN2NmNDNkMjU0OTVhOWIyOGFhZTAzYjkwZDZjOSIsImlhdCI6MTc1Mzk5NTU2OCwiZXhwIjoyMDY5MzU1NTY4fQ.7PSSyrh2hnUxccoXIYG8QAbjEU4yMudd4SVfRLZw0AI=$(jq -r '.ha_token' /data/options.json)

python3 /bot.py
