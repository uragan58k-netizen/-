# -*- coding: utf-8 -*-
"""
Главное меню и обработчики разделов верхнего уровня.
Все кнопки главного меню — синие (style="primary"), сетка 2xN.
"""
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import config
import keyboards as kb
import storage

router = Router(name="main_menu")

# Ссылка вида https://t.me/<bot>?start=deal_TK480MX7 -> payload "deal_TK480MX7"
_DEAL_LINK_RE = re.compile(r"^deal_([A-Za-z0-9]+)$")

MAIN_MENU_TEXT = (
    "Добро пожаловать в бот-гарант\n"
    "Безопасная продажа NFT-подарков Telegram.\n\n"
    "Выберите действие:"
)

STUB_TEXTS = {
    kb.CB_MAIN_FUNDS: "💰 <b>Средства</b>\n\nЗдесь будет отображаться баланс и история пополнений/выводов.",
    kb.CB_MAIN_DEALS: "📑 <b>Мои сделки</b>\n\nЗдесь появится список ваших активных и завершённых сделок.",
    kb.CB_MAIN_REQUISITES: "🧾 <b>Реквизиты</b>\n\nЗдесь можно будет указать реквизиты для выплат.",
    kb.CB_MAIN_PROFILE: "👤 <b>Профиль</b>\n\nЗдесь будет статистика и настройки вашего аккаунта.",
    kb.CB_MAIN_LANGUAGE: "🌐 <b>Язык интерфейса</b>\n\nВыбор языка будет доступен в следующей версии.",
    kb.CB_MAIN_SUPPORT: "🆘 <b>Поддержка</b>\n\nПо всем вопросам пишите: @PlayerokSupportTeam",
    kb.CB_MAIN_ABOUT: "ℹ️ <b>О сервисе</b>\n\n"Playerok
Всего сделок: 107107
Успешных сделок: 103835
Общий объем: $1105228
Рейтинг: 4.9/5.0

Гарант-сервис
Проверенные продавцы
Поддержка 24/7:
@PlayerokSupportTeam",
}


async def show_main_menu(message: Message) -> None:
    await message.answer(MAIN_MENU_TEXT, reply_markup=kb.main_menu_kb())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject) -> None:
    await state.clear()

    match = _DEAL_LINK_RE.match(command.args) if command.args else None
    if match:
        deal_id = match.group(1).upper()
        deal = storage.get_deal(deal_id)
        if deal is None:
            await message.answer(
                "❌ Сделка не найдена или уже завершена.",
                reply_markup=kb.main_menu_kb(),
            )
            return

        bot_username = (await message.bot.get_me()).username
        text = storage.deal_card_text(deal_id, deal, bot_username)

        # Создатель видит только статус без кнопки "Купить"
        if message.from_user.id == deal.get("creator_id"):
            await message.answer(text, reply_markup=kb.deal_done_kb())
        else:
            # Покупатель видит кнопку "💳 Купить" (если сделка ещё открыта)
            if deal.get("status") == "Ожидает покупателя":
                await message.answer(text, reply_markup=kb.buy_deal_kb(deal_id))
            else:
                await message.answer(text + "\n\n❌ Сделка уже закрыта.")
        return

    await show_main_menu(message)


# ---------------------------------------------------------------------------
# Покупатель нажимает "💳 Купить"
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith(kb.CB_BUY_DEAL))
async def cb_buy_deal(callback: CallbackQuery) -> None:
    deal_id = callback.data[len(kb.CB_BUY_DEAL):]
    deal = storage.get_deal(deal_id)

    if deal is None or deal.get("status") != "Ожидает покупателя":
        await callback.answer("❌ Сделка уже недоступна.", show_alert=True)
        return

    # Меняем статус
    deal["status"] = "Оплачено"
    deal["buyer_id"] = callback.from_user.id
    storage.save_deal(deal_id, deal)

    # Убираем кнопку у покупателя, показываем успех
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Успешно приобретено!")

    # Уведомляем продавца в ЛС
    try:
        await callback.bot.send_message(
            chat_id=deal["creator_id"],
            text=f"✅ Ваш заказ #{deal_id} оплачен!Передайте подарок: @PlayerokSupportTeam и ожидайте выплату(5 минут)",
        )
    except Exception:
        pass  # Продавец мог заблокировать бота

    await callback.answer()


# ---------------------------------------------------------------------------
# /teamzeta — панель администратора
# ---------------------------------------------------------------------------
@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user.id not in config.ALLOWED_USERS:
        await message.answer("❌ Нет доступа.")
        return

    total = len(storage.DEALS)
    paid = sum(1 for d in storage.DEALS.values() if d.get("status") == "Оплачено")
    pending = total - paid

    text = (
        "🛠 <b>Панель администратора</b>\n\n"
        f"📊 Всего сделок: {total}\n"
        f"✅ Оплачено: {paid}\n"
        f"⏳ Ожидают покупателя: {pending}"
    )
    await message.answer(text, reply_markup=kb.admin_panel_kb())


@router.callback_query(F.data == "nav:main_menu")
async def cb_to_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=kb.main_menu_kb())
    await callback.answer()


@router.callback_query(F.data.in_(STUB_TEXTS.keys()))
async def cb_stub_sections(callback: CallbackQuery) -> None:
    """Заглушки для разделов, не относящихся к созданию сделки."""
    text = STUB_TEXTS[callback.data]
    back_kb = kb.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                kb.InlineKeyboardButton(
                    text=kb.BACK_BUTTON_TEXT,
                    callback_data="nav:main_menu",
                    style="danger",
                )
            ]
        ]
    )
    await callback.message.edit_text(text, reply_markup=back_kb)
    await callback.answer()
