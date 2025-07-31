# BNK_BOT_2 — Telegram бот для Home Assistant

Этот бот собирает отчёты из Telegram-группы, сохраняет их в CSV, ведёт статистику и работает как Home Assistant Add-on.

## Настройка

1. Установите Add-on через Custom Repository в Home Assistant.
2. В конфигурации Add-on укажите ваш `telegram_token`.
3. Запустите бота.

## Поддерживаемые команды

- `/csv` — получить CSV-файл
- `/сброс` — сбросить все данные
- `/статистика` — сводная статистика