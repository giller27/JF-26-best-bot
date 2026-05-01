# src/bot/handlers/admin.py
from aiogram import Router, F, types
from src.core.database import db
from src.core.config import settings

admin_router = Router()

# Middleware або фільтр для перевірки на адміна
@admin_router.message(F.from_user.id.in_(settings.ADMIN_IDS), F.text == "/admin")
async def admin_panel(message: types.Message):
    count = await db.db.registrations.count_documents({})
    vntu_count = await db.db.registrations.count_documents({"is_vntu": True})
    
    stats_text = (
        "📊 **Статистика івенту**\n\n"
        f"Всього реєстрацій: {count}\n"
        f"З них ВНТУ: {vntu_count}\n"
    )
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📢 Зробити розсилку", callback_data="broadcast")],
        [types.InlineKeyboardButton(text="📥 Експорт в CSV", callback_data="export_csv")]
    ])
    
    await message.answer(stats_text, reply_markup=kb, parse_mode="Markdown")

@admin_router.callback_query(F.data == "export_csv")
async def export_data(callback: types.CallbackQuery):
    users = await db.db.registrations.find().to_list(length=None)
    # Тут логіка генерації CSV файлу за допомогою модуля csv або pandas
    # ...
    await callback.message.answer("Файл готується...")