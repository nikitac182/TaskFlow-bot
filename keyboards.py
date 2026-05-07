from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мои задачи")],
        [KeyboardButton(text="Отправить выполнение")],
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

on_tasks_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выполнил"), KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True,
)

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить задачу", callback_data="add_task")],

        [InlineKeyboardButton(text="Изменить номер", callback_data="change_number") ],

        [
            InlineKeyboardButton(text="Пользователи", callback_data="users"),
            InlineKeyboardButton(text="Админы", callback_data="admins")  
        ],

        [InlineKeyboardButton(text="Задания", callback_data="tasks") ],

        [InlineKeyboardButton(text="Заявки", callback_data="requests") ],
    ],
    resize_keyboard=True,
)