from typing import Optional
import re
from aiogram import BaseMiddleware
from cachetools import TTLCache

BANNED_WORDS = ["мат1", "мат2", "badword"] # Можна винести в БД/файл

class DataValidator:
    @staticmethod
    def validate_name(name: str) -> bool:
        # Очищення від обфускації (пробіли, спецсимволи)
        clean_name = re.sub(r'[^a-zA-Zа-яА-ЯіїєґІЇЄҐ]', '', name).lower()
        for word in BANNED_WORDS:
            if word in clean_name:
                return False
        return len(name) >= 2

    @staticmethod
    def normalize_phone(phone: str) -> Optional[str]:
        # Залишаємо лише цифри
        digits = re.sub(r'\D', '', phone)
        # Підтримуємо формати:
        # +380XXXXXXXXX, 380XXXXXXXXX, 0XXXXXXXXX, XXXXXXXXX (9 digits starting with 9)
        res = None
        if digits.startswith('380') and len(digits) == 12:
            res = digits
        elif digits.startswith('0') and len(digits) == 10:
            # 0XXXXXXXXX -> 38 0XXXXXXXXX -> 380XXXXXXXXX
            res = f"38{digits}"
        elif len(digits) == 9 and digits.startswith('9'):
            # e.g. 9XXXXXXXX -> 3809XXXXXXXX
            res = f"38{digits}"
        else:
            return None

        # Перевірка кодів операторів України (поширені мобільні коди)
        valid_codes = (
            '039','050','063','066','067','068',
            '091','092','093','094','095','096','097','098','099','089'
        )

        if not any(res.startswith(f"38{code}") for code in valid_codes):
            return None

        # Повертаємо у форматі E.164: +380XXXXXXXXX
        return f"+{res}"


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit=2):
        self.cache = TTLCache(maxsize=10000, ttl=limit)

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        if user_id in self.cache:
            return # Ігноруємо повідомлення
        self.cache[user_id] = True
        return await handler(event, data)