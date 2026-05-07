import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher
from const import TOKEN
from routers.user import router as user_router, setup_router
from routers.admin import router as admin_router, register_admin_commands

tasks = {
    "1": "Задание №1:\nПодпишись на канал и отправь скрин",
    "2": "Задание №2:\nПоставь лайк под постом",
    "3": "Задание №3:\nПригласи друга",
    "4": "Задание №4:\nЗайди на сайт бота",
    "5": "Задание №5:\n..."
}


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(user_router)
db = None

async def main():
    global db

    db = await aiosqlite.connect("sqlite.db")

    setup_router(bot=bot, db=db, tasks=tasks)
    register_admin_commands(dp, db)

    await db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        phone TEXT
    )
    """
    )

    await db.commit()
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(main())
