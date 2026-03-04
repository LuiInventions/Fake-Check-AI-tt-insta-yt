#!/bin/bash
source fakecheck/.env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN is strictly required in .env file."
    exit 1
fi

if [ -z "$TELEGRAM_WEBHOOK_URL" ]; then
    echo "Error: TELEGRAM_WEBHOOK_URL is missing in .env. Example: https://deine-domain.com/api/telegram/webhook"
    exit 1
fi

curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" -H "Content-Type: application/json" -d "{\"url\": \"${TELEGRAM_WEBHOOK_URL}\"}"
echo ""
echo "Webhook has been set."
