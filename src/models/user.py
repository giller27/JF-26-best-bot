from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class UserRegistration(BaseModel):
    user_id: int = Field(..., example=12345678)
    username: Optional[str] = None
    first_name: str
    last_name: str
    phone: str  # Буде нормалізовано через валідатор
    email: EmailStr
    university: str
    source: str  # Звідки дізналися
    event_days: str  # "day_1", "day_2", "both"
    is_vntu: bool = False
    registered_at: datetime = Field(default_factory=datetime.utcnow)

class EventSettings(BaseModel):
    event_name: str
    event_date: datetime
    location: str
    vntu_promo_text: str = "Якщо ти з ВНТУ — ходімо до BEST!"
    reminder_texts: dict = {
        "1_day": "Завтра івент!",
        "3_hours": "Залишилось 3 години!",
        "1_hour": "Починаємо за годину!"
    }