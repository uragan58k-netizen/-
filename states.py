# -*- coding: utf-8 -*-
"""
Состояния FSM для сценария создания сделки:

Роль -> Тип сделки -> Описание предмета сделки -> Способ оплаты
     -> Сумма -> Номер карты -> Готово
"""
from aiogram.fsm.state import State, StatesGroup


class DealCreation(StatesGroup):
    choosing_role = State()         # Продавец / Покупатель
    choosing_deal_type = State()    # Аккаунт / NFT Gifts / Канал
    entering_description = State()  # Описание предмета сделки (текст)
    choosing_currency = State()     # Способ оплаты
    entering_amount = State()       # Сумма (только целое число)
    entering_card = State()         # Номер карты (13-16 цифр)
