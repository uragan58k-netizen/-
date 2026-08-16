# -*- coding: utf-8 -*-
"""
Конфигурация бота.
Вставьте токен, полученный у @BotFather, в переменную BOT_TOKEN
или задайте переменную окружения BOT_TOKEN перед запуском.
"""
import os

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "ВСТАВЬТЕ_СЮДА_ТОКЕН_БОТА")

# Список Telegram ID администраторов (вы и ваш друг).
# Узнать свой ID можно у @userinfobot
ALLOWED_USERS: list[int] = [
    123456789,   # <- замените на свой Telegram ID
    987654321,   # <- замените на ID друга
]
