# src/services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from src.core.database import db

scheduler = AsyncIOScheduler()

async def send_reminder(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f"Failed to send reminder to {user_id}: {e}")

async def schedule_event_reminders(bot, event_time, event_details):
    # Отримуємо всіх користувачів
    users = await db.db.registrations.find().to_list(length=None)
    
    # Часи для нагадувань
    times = {
        "1 day before": event_time - timedelta(days=1),
        "3 hours before": event_time - timedelta(hours=3),
        "1 hour before": event_time - timedelta(hours=1)
    }

    for label, run_time in times.items():
        if run_time > datetime.now():
            for user in users:
                scheduler.add_job(
                    send_reminder,
                    'date',
                    run_date=run_time,
                    args=[bot, user['user_id'], f"Нагадування: {event_details}\nЧас: {label}"]
                )