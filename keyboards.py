from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Задания")],
        [KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Вывод")],
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
    ]
)

