from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    MONGO_URL: str = "mongodb://mongodb:27017"
    DB_NAME: str = "event_db"
    ADMIN_IDS: str  # Передаємо через кому: "123,456"
    
    @property
    def admin_list(self):
        return [int(x) for x in self.ADMIN_IDS.split(",") if x]

    class Config:
        env_file = ".env"

settings = Settings()