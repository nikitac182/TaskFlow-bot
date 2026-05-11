from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мои задачи")],
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Поддержка")],
    ],
    resize_keyboard=True,
)

tasks_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2")],
        [KeyboardButton(text="3")],
        [KeyboardButton(text="4")],
        [KeyboardButton(text="Назад")]
    ], 
    resize_keyboard=True,
)

back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Выполнить", callback_data="make_task")],
        [InlineKeyboardButton(text="⬅️", callback_data="p_back")]
    ]
)

back_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data="p_back_2")]
    ]
)

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пользователи", callback_data='admin_users_menu')
        ],
        [
            InlineKeyboardButton(text="Задачи", callback_data='admin_tasks_menu')
        ]
    ],
)
admin_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Выдать задачу", callback_data='admin_give_task')
        ],
        [
            InlineKeyboardButton(text="❌ Удалить пользователя", callback_data='admin_delete_user')
        ],
        [
            InlineKeyboardButton(text="🛡 Сделать админом", callback_data='admin_make_admin')
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data='admin_users_back')
        ],
    ],
)

admin_back_kb_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data='admin_users_back')
        ],
    ],
)