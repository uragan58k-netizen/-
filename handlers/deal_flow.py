# -*- coding: utf-8 -*-
"""
Сценарий создания сделки (FSM, хранение состояний — MemoryStorage):

    Главное меню
        -> [choosing_role]         Выбор роли: Продавец / Покупатель
        -> [choosing_deal_type]    Выбор типа сделки: Аккаунт / NFT Gifts / Канал
        -> [entering_description]  Описание предмета сделки (Ссылку на NFT подарок, аккаунт или канал)
        -> [choosing_currency]     Выбор способа оплаты
        -> [entering_amount]       Сумма (только целое число)
        -> [entering_card]         Номер карты (13-16 цифр)
        -> Карточка созданной сделки

Красная кнопка "◀️ Назад" (style="danger") есть на каждом шаге и
возвращает пользователя на один шаг назад, используя карту переходов
в go_back(). С первого шага сценария "Назад" ведёт в главное меню.
"""
import random
import re
import string

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards as kb
import storage
from handlers.main_menu import MAIN_MENU_TEXT
from states import DealCreation

router = Router(name="deal_flow")

ROLE_LABELS = {"seller": "🛒 Продавец", "buyer": "💳 Покупатель"}

# callback_data вида "deal_type:account" -> ключ "account"
_TYPE_CALLBACKS = {
    kb.CB_TYPE_ACCOUNT: "account",
    kb.CB_TYPE_NFT_GIFTS: "nft_gifts",
    kb.CB_TYPE_CHANNEL: "channel",
}

_CURRENCY_CALLBACKS = {
    kb.CB_CURRENCY_RUB: "RUB",
    kb.CB_CURRENCY_UAH: "UAH",
    kb.CB_CURRENCY_BYN: "BYN",
    kb.CB_CURRENCY_STARS: "XTR",
    kb.CB_CURRENCY_USDT: "USDT",
    kb.CB_CURRENCY_TON: "TON",
    kb.CB_CURRENCY_OTHER: "OTHER",
}


def _gen_deal_id() -> str:
    """Короткий код сделки вида TK480MX7. Проверяем на коллизии
    с уже существующими сделками в storage.DEALS."""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        deal_id = "".join(random.choices(alphabet, k=8))
        if deal_id not in storage.DEALS:
            return deal_id


def _role_summary(data: dict) -> str:
    lines = []
    if "role" in data:
        lines.append(f"Роль: {ROLE_LABELS[data['role']]}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Шаг 0 -> Шаг 1: старт сценария
# ---------------------------------------------------------------------------
@router.callback_query(F.data == kb.CB_MAIN_CREATE_DEAL)
async def start_deal_creation(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DealCreation.choosing_role)
    await callback.message.edit_text(
        "🤝 <b>Создание сделки</b>\n\nВыберите свою роль в сделке:",
        reply_markup=kb.role_selection_kb(),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# Шаг 1 -> Шаг 2: роль выбрана
# ---------------------------------------------------------------------------
@router.callback_query(DealCreation.choosing_role, F.data.in_((kb.CB_ROLE_SELLER, kb.CB_ROLE_BUYER)))
async def choose_role(callback: CallbackQuery, state: FSMContext) -> None:
    role = callback.data.split(":")[1]
    await state.update_data(role=role)
    await state.set_state(DealCreation.choosing_deal_type)

    await callback.message.edit_text("Выберите тип сделки:", reply_markup=kb.deal_type_kb())
    await callback.answer()


# ---------------------------------------------------------------------------
# Шаг 2 -> Шаг 3: тип сделки выбран -> просим описание текстом
# ---------------------------------------------------------------------------
@router.callback_query(DealCreation.choosing_deal_type, F.data.in_(_TYPE_CALLBACKS.keys()))
async def choose_deal_type(callback: CallbackQuery, state: FSMContext) -> None:
    deal_type = _TYPE_CALLBACKS[callback.data]
    await state.update_data(deal_type=deal_type)
    await state.set_state(DealCreation.entering_description)

    text = (
        "Опишите предмет сделки.\n"
        "Ссылку на NFT подарок, аккаунт или канал"
    )
    await callback.message.edit_text(text, reply_markup=kb.description_step_kb())
    await callback.answer()


# ---------------------------------------------------------------------------
# Шаг 3: описание введено текстом -> выбор способа оплаты
# ---------------------------------------------------------------------------
@router.message(DealCreation.entering_description, F.text)
async def enter_description(message: Message, state: FSMContext) -> None:
    description = message.text.strip()
    if not description:
        await message.answer(
            "⚠️ Описание не может быть пустым. Опишите предмет сделки текстом.",
            reply_markup=kb.description_step_kb(),
        )
        return

    await state.update_data(description=description)
    await state.set_state(DealCreation.choosing_currency)
    await message.answer("Выберите способ оплаты:", reply_markup=kb.currency_selection_kb())


# ---------------------------------------------------------------------------
# Шаг 4 -> Шаг 5: способ оплаты выбран -> просим сумму
# ---------------------------------------------------------------------------
@router.callback_query(DealCreation.choosing_currency, F.data.in_(_CURRENCY_CALLBACKS.keys()))
async def choose_currency(callback: CallbackQuery, state: FSMContext) -> None:
    currency = _CURRENCY_CALLBACKS[callback.data]
    await state.update_data(currency=currency)
    await state.set_state(DealCreation.entering_amount)

    text = f"Введите сумму в {currency}. Только целое число."
    await callback.message.edit_text(text, reply_markup=kb.amount_step_kb())
    await callback.answer()


# ---------------------------------------------------------------------------
# Шаг 5: сумма введена текстом (целое число) -> просим номер карты
# ---------------------------------------------------------------------------
@router.message(DealCreation.entering_amount, F.text)
async def enter_amount(message: Message, state: FSMContext) -> None:
    raw = message.text.strip().replace(" ", "")
    if not raw.isdigit() or int(raw) <= 0:
        data = await state.get_data()
        currency = data.get("currency", "")
        await message.answer(
            f"⚠️ Введите сумму в {currency} целым числом, например: 1500",
            reply_markup=kb.amount_step_kb(),
        )
        return

    await state.update_data(amount=int(raw))
    await state.set_state(DealCreation.entering_card)
    await message.answer("Введите номер карты (13-16 цифр).", reply_markup=kb.card_step_kb())


# ---------------------------------------------------------------------------
# Шаг 6: номер карты введён текстом -> создаём сделку
# ---------------------------------------------------------------------------
@router.message(DealCreation.entering_card, F.text)
async def enter_card(message: Message, state: FSMContext) -> None:
    raw = re.sub(r"[\s-]", "", message.text.strip())
    if not raw.isdigit() or not (13 <= len(raw) <= 16):
        await message.answer(
            "⚠️ Номер карты должен содержать от 13 до 16 цифр. Попробуйте снова.",
            reply_markup=kb.card_step_kb(),
        )
        return

    await state.update_data(card=raw)
    data = await state.get_data()
    await state.clear()

    deal_id = _gen_deal_id()
    data["status"] = "Ожидает покупателя"
    data["creator_id"] = message.from_user.id
    storage.save_deal(deal_id, data)

    bot_username = (await message.bot.get_me()).username
    text = storage.deal_card_text(deal_id, data, bot_username)
    await message.answer(text, reply_markup=kb.deal_done_kb())


# ---------------------------------------------------------------------------
# Универсальная красная кнопка "Назад" — карта переходов по шагам FSM
# ---------------------------------------------------------------------------
@router.callback_query(F.data == kb.CB_BACK)
async def go_back(callback: CallbackQuery, state: FSMContext) -> None:
    current = await state.get_state()
    data = await state.get_data()

    if current == DealCreation.choosing_role.state:
        # Первый шаг сценария -> возврат в главное меню
        await state.clear()
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=kb.main_menu_kb())

    elif current == DealCreation.choosing_deal_type.state:
        await state.set_state(DealCreation.choosing_role)
        text = "🤝 <b>Создание сделки</b>\n\nВыберите свою роль в сделке:"
        await callback.message.edit_text(text, reply_markup=kb.role_selection_kb())

    elif current == DealCreation.entering_description.state:
        await state.set_state(DealCreation.choosing_deal_type)
        await callback.message.edit_text("Выберите тип сделки:", reply_markup=kb.deal_type_kb())

    elif current == DealCreation.choosing_currency.state:
        await state.set_state(DealCreation.entering_description)
        text = (
            "Опишите предмет сделки.\n"
            "Ссылку на NFT подарок, аккаунт или канал"
        )
        await callback.message.edit_text(text, reply_markup=kb.description_step_kb())

    elif current == DealCreation.entering_amount.state:
        await state.set_state(DealCreation.choosing_currency)
        await callback.message.edit_text("Выберите способ оплаты:", reply_markup=kb.currency_selection_kb())

    elif current == DealCreation.entering_card.state:
        currency = data.get("currency", "")
        await state.set_state(DealCreation.entering_amount)
        text = f"Введите сумму в {currency}. Только целое число."
        await callback.message.edit_text(text, reply_markup=kb.amount_step_kb())

    else:
        # Неизвестное/пустое состояние (например, после завершения сделки)
        # -> безопасный возврат в главное меню.
        await state.clear()
        await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=kb.main_menu_kb())

    await callback.answer()
