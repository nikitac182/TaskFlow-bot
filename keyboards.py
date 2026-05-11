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
            InlineKeyboardButton(text="Пользователи", callback_data='users_info')
        ],
        [
            InlineKeyboardButton(text="Задачи", callback_data='tasks_1')
        ]
    ],

)