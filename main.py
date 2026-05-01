import asyncio
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn
from src.core.config import settings
from src.core.database import db
from src.bot.handlers import registration, admin as bot_admin
from src.api.routes import admin_web
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Реєстрація роутерів бота
dp.include_router(registration.router)
dp.include_router(bot_admin.admin_router)

# Життєвий цикл FastAPI (запускає базу і бота до старту сервера)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Підключення до БД...")
    await db.connect()
    
    print("Запуск Telegram-бота...")
    asyncio.create_task(dp.start_polling(bot))
    
    yield  # Тут сервер працює
    
    print("Зупинка...")
    await bot.session.close()

# Створення додатку FastAPI
app = FastAPI(lifespan=lifespan)

# === ОСЬ НАША МАГІЯ: Кладемо бота в пам'ять сервера ===
app.state.bot = bot 

# Реєстрація веб-роутерів
app.include_router(admin_web.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)