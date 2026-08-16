# Escrow Telegram-бот (aiogram 3.x, цветные кнопки Bot API 9.4+)

Бот-гарант сделок с интерфейсом на инлайн-кнопках, использующих
свойство `style` (`primary` / `success` / `danger`), появившееся в
Telegram Bot API 9.4 и поддерживаемое `aiogram` начиная с версии 3.20.

## Структура проекта

```
escrow_bot/
├── bot.py                  # точка входа, запуск polling
├── config.py                # токен бота (BOT_TOKEN)
├── states.py                 # FSM-состояния сценария создания сделки
├── keyboards.py               # все инлайн-клавиатуры со style="primary/success/danger"
├── requirements.txt
└── handlers/
    ├── __init__.py           # сборка общего роутера
    ├── main_menu.py           # /start, главное меню, заглушки разделов
    └── deal_flow.py            # FSM-сценарий создания сделки + кнопка "Назад"
```

## Как работает раскраска кнопок

Правило дизайна реализовано через параметр `style` у `InlineKeyboardButton`:

| Экран                                   | Кнопки                          | style       | Цвет   |
|------------------------------------------|----------------------------------|-------------|--------|
| Главное меню                              | Создать сделку, Средства, Сделки, Реквизиты, Профиль, Язык, Поддержка, О сервисе | `primary`  | 🔵 синий  |
| Любой вложенный экран (низ, во всю ширину) | ◀️ Назад                         | `danger`    | 🔴 красный |
| Выбор валюты                               | Рубли, USDT                      | `success`   | 🟢 зелёный |

```python
InlineKeyboardButton(text="Создать сделку", callback_data="main:create_deal", style="primary")
InlineKeyboardButton(text="◀️ Назад", callback_data="nav:back", style="danger")
InlineKeyboardButton(text="Рубли", callback_data="currency:rub", style="success")
```

Если Telegram-клиент пользователя ещё не поддерживает Bot API 9.4,
`style` просто игнорируется и кнопка отображается в стандартном виде —
функциональность не ломается.

## Сценарий FSM (MemoryStorage)

```
Главное меню
   │  "Создать сделку" (синяя)
   ▼
choosing_role        — Продавец / Покупатель
   │
   ▼
choosing_deal_type    — Товар / Услуга / Цифровой продукт / Другое
   │
   ▼
choosing_currency      — Рубли / USDT   (зелёные кнопки)
   │
   ▼
entering_amount          — сумма вводится текстовым сообщением
   │
   ▼
Подтверждение сделки → главное меню
```

На каждом шаге красная кнопка «◀️ Назад» отправляет `callback_data="nav:back"`.
Единый обработчик `go_back()` в `handlers/deal_flow.py` смотрит на текущее
состояние (`state.get_state()`) и по карте переходов возвращает пользователя
на предыдущий экран, подставляя ранее сохранённые данные (`state.get_data()`).
С первого шага сценария (`choosing_role`) кнопка «Назад» возвращает в главное меню.

## Запуск

```bash
pip install -r requirements.txt

# укажите токен, полученный у @BotFather
export BOT_TOKEN="123456:AA...your_token"   # Linux/macOS
# или на Windows (PowerShell):
# $env:BOT_TOKEN="123456:AA...your_token"

python bot.py
```

Либо впишите токен прямо в `config.py` вместо переменной окружения.

## Требования

- Python 3.10+
- `aiogram>=3.20.0` (в этой версии добавлена поддержка `style` и `icon_custom_emoji_id`)
- Клиент Telegram, поддерживающий Bot API 9.4+, для отображения цвета кнопок
  (в старых клиентах кнопки останутся рабочими, но нейтрального цвета)
