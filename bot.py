# bot.py
import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher
from const import TOKEN
import routers.user as user_module
import routers.admin as admin_module
import routers.callbacks as callbacks_module
from middlewares.db_middleware import DbMiddleware

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    db = await aiosqlite.connect("sqlite.db")

    await db.executescript(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_admin BOOLEAN
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        status TEXT DEFAULT "new",
        assigned_to INTEGER,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        materials TEXT,
        deadline TEXT
    );
    
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        user_id INTEGER,
        text TEXT,
        file_id INTEGER,
        status TEXT DEFAULT "in_progress",
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        type TEXT
    );

    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    )
    await db.commit()

    # Передаём db через middleware — так он доступен везде включая фильтры
    middleware = DbMiddleware(db=db)
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)

    user_module.bot = bot
    user_module.db = db

    admin_module.bot = bot
    admin_module.db = db

    callbacks_module.bot = bot
    callbacks_module.db = db

    dp.include_router(callbacks_module.router)
    dp.include_router(admin_module.router)
    dp.include_router(user_module.router)

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(main())
