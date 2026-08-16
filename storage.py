# -*- coding: utf-8 -*-
"""
Простое in-memory хранилище созданных сделок (без базы данных).

Ключ  — код сделки, например "TK480MX7".
Значение — словарь с данными сделки (role, deal_type, description,
currency, amount, card, status, creator_id).

Вынесено в отдельный модуль, чтобы к нему могли обращаться и
handlers/deal_flow.py (создание сделки), и handlers/main_menu.py
(обработка диплинка ?start=deal_XXXXXXXX) без циклических импортов.
"""
from typing import Any, Optional

DEALS: dict[str, dict[str, Any]] = {}


def save_deal(deal_id: str, data: dict[str, Any]) -> None:
    DEALS[deal_id] = data


def get_deal(deal_id: str) -> Optional[dict[str, Any]]:
    return DEALS.get(deal_id)


def deal_link(bot_username: str, deal_id: str) -> str:
    return f"https://t.me/{bot_username}?start=deal_{deal_id}"


def deal_card_text(deal_id: str, data: dict[str, Any], bot_username: str) -> str:
    """Карточка сделки — тот же текст, что видит и создатель сразу
    после создания, и покупатель, перешедший по ссылке."""
    return (
        f"✅ Сделка #{deal_id} создана\n"
        f"Тип: {data['deal_type']}\n"
        f"Описание: {data['description']}\n"
        f"Сумма: {data['amount']} {data['currency']}\n"
        f"Статус: {data.get('status', 'Ожидает покупателя')}\n"
        f"🔗 Ссылка для покупателя:\n"
        f"{deal_link(bot_username, deal_id)}\n\n"
        "⚠️ Все сделки проводятся строго внутри бота. "
        "Сделки в чатах — мошенничество!\n"
        "Комиссия сервиса — 2%"
    )
