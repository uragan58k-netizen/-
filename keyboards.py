# -*- coding: utf-8 -*-
"""
Клавиатуры бота.

Используется свойство `style` InlineKeyboardButton (Telegram Bot API 9.4+,
поддерживается aiogram 3.20+):
    style="primary"  -> синяя кнопка   (основные действия)
    style="success"  -> зелёная кнопка (позитивные действия)
    style="danger"   -> красная кнопка (деструктивные действия / "Назад")

Если клиент пользователя не поддерживает Bot API 9.4, Telegram
автоматически отобразит кнопку в стандартном (нейтральном) виде —
функциональность при этом не теряется.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ---------------------------------------------------------------------------
# Callback data
# ---------------------------------------------------------------------------
CB_MAIN_CREATE_DEAL = "main:create_deal"
CB_MAIN_FUNDS = "main:funds"
CB_MAIN_DEALS = "main:deals"
CB_MAIN_REQUISITES = "main:requisites"
CB_MAIN_PROFILE = "main:profile"
CB_MAIN_LANGUAGE = "main:language"
CB_MAIN_SUPPORT = "main:support"
CB_MAIN_ABOUT = "main:about"

CB_ROLE_SELLER = "role:seller"
CB_ROLE_BUYER = "role:buyer"

CB_TYPE_ACCOUNT = "deal_type:account"
CB_TYPE_NFT_GIFTS = "deal_type:nft_gifts"
CB_TYPE_CHANNEL = "deal_type:channel"

CB_CURRENCY_RUB = "currency:RUB"
CB_CURRENCY_UAH = "currency:UAH"
CB_CURRENCY_BYN = "currency:BYN"
CB_CURRENCY_STARS = "currency:XTR"
CB_CURRENCY_USDT = "currency:USDT"
CB_CURRENCY_TON = "currency:TON"
CB_CURRENCY_OTHER = "currency:OTHER"

CB_BACK = "nav:back"
CB_BUY_DEAL = "deal:buy:"       # + deal_id в конце: "deal:buy:TK480MX7"
CB_ADMIN_PANEL = "admin:panel"

BACK_BUTTON_TEXT = "◀️ Назад"

# Отображаемые подписи типов сделки (для текста внутри сообщений)
DEAL_TYPE_LABELS = {
    "account": "👤 Аккаунт",
    "nft_gifts": "🎁 NFT Gifts",
    "channel": "📢 Канал",
}

# Отображаемые подписи способов оплаты
CURRENCY_LABELS = {
    "RUB": "✅ Рубли",
    "UAH": "💳 Гривны",
    "BYN": "💳 BYN",
    "XTR": "⭐ Stars",
    "USDT": "💲 USDT",
    "TON": "💎 TON",
    "OTHER": "❓ Другая валюта",
}


def _back_row() -> list[InlineKeyboardButton]:
    """Красная кнопка «Назад», растянутая на всю ширину (отдельный ряд)."""
    return [
        InlineKeyboardButton(
            text=BACK_BUTTON_TEXT,
            callback_data=CB_BACK,
            style="danger",
        )
    ]


# ---------------------------------------------------------------------------
# Главное меню — все кнопки синие (style="primary"), сетка 2xN
# ---------------------------------------------------------------------------
def main_menu_kb() -> InlineKeyboardMarkup:
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()

    buttons = [
        ("💼 Создать сделку", CB_MAIN_CREATE_DEAL),
        ("💰 Средства", CB_MAIN_FUNDS),
        ("📑 Сделки", CB_MAIN_DEALS),
        ("🧾 Реквизиты", CB_MAIN_REQUISITES),
        ("👤 Профиль", CB_MAIN_PROFILE),
        ("🌐 Язык", CB_MAIN_LANGUAGE),
        ("🆘 Поддержка", CB_MAIN_SUPPORT),
        ("ℹ️ О сервисе", CB_MAIN_ABOUT),
    ]

    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data, style="primary")

    builder.adjust(2)  # сетка по 2 кнопки в ряд
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Шаг 1: выбор роли — Продавец / Покупатель (синие) + красная "Назад"
# ---------------------------------------------------------------------------
def role_selection_kb() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🛒 Продавец", callback_data=CB_ROLE_SELLER, style="primary"),
            InlineKeyboardButton(text="💳 Покупатель", callback_data=CB_ROLE_BUYER, style="primary"),
        ],
        _back_row(),
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------------------------------------------------------------------
# Шаг 2: выбор типа сделки — Аккаунт / NFT Gifts / Канал (каждая кнопка
# на всю ширину, синие) + красная "Назад"
# ---------------------------------------------------------------------------
def deal_type_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=DEAL_TYPE_LABELS["account"], callback_data=CB_TYPE_ACCOUNT, style="primary")],
        [InlineKeyboardButton(text=DEAL_TYPE_LABELS["nft_gifts"], callback_data=CB_TYPE_NFT_GIFTS, style="primary")],
        [InlineKeyboardButton(text=DEAL_TYPE_LABELS["channel"], callback_data=CB_TYPE_CHANNEL, style="primary")],
        _back_row(),
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------------------------------------------------------------------
# Шаг 3 (текстовый ввод описания сделки) — только кнопка "Назад"
# ---------------------------------------------------------------------------
def description_step_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back_row()])


# ---------------------------------------------------------------------------
# Шаг 4: выбор способа оплаты — каждая кнопка на всю ширину, синие
# (style="primary") + красная "Назад"
# ---------------------------------------------------------------------------
def currency_selection_kb() -> InlineKeyboardMarkup:
    order = ["RUB", "UAH", "BYN", "XTR", "USDT", "TON", "OTHER"]
    cb_map = {
        "RUB": CB_CURRENCY_RUB,
        "UAH": CB_CURRENCY_UAH,
        "BYN": CB_CURRENCY_BYN,
        "XTR": CB_CURRENCY_STARS,
        "USDT": CB_CURRENCY_USDT,
        "TON": CB_CURRENCY_TON,
        "OTHER": CB_CURRENCY_OTHER,
    }
    rows = [
        [InlineKeyboardButton(text=CURRENCY_LABELS[code], callback_data=cb_map[code], style="primary")]
        for code in order
    ]
    rows.append(_back_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------------------------------------------------------------------
# Шаг 5 (ввод суммы текстом) — только кнопка "Назад"
# ---------------------------------------------------------------------------
def amount_step_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back_row()])


# ---------------------------------------------------------------------------
# Шаг 6 (ввод номера карты текстом) — только кнопка "Назад"
# ---------------------------------------------------------------------------
def card_step_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back_row()])


# ---------------------------------------------------------------------------
# Финальный экран созданной сделки — только кнопка "Назад" (в главное меню)
# ---------------------------------------------------------------------------
def deal_done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_back_row()])


# ---------------------------------------------------------------------------
# Карточка сделки для покупателя — кнопка "💳 Купить"
# ---------------------------------------------------------------------------
def buy_deal_kb(deal_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Купить",
                    callback_data=f"{CB_BUY_DEAL}{deal_id}",
                    style="primary",
                )
            ]
        ]
    )


# ---------------------------------------------------------------------------
# Админ-панель
# ---------------------------------------------------------------------------
def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_back_row()[0]]
        ]
    )
