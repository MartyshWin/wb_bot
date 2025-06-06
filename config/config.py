from pathlib import Path
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    token: SecretStr  # будет загружен из .env через Settings
    parse_mode: str = "HTML"
    admins: list[int] = Field(default_factory=list)
    use_webhook: bool = False
    webhook_url: str | None = None
    retry_on_failure: bool = True


class LoggingSettings(BaseModel):
    level: str = "INFO"
    log_to_file: bool = True
    logs_dir: Path = Path("logs")


class YooKassaSettings(BaseModel):
    shop_id: str                     # ID магазина в ЮKassa
    secret: SecretStr                # Секретный ключ
    currency: str = "RUB"            # Валюта по‑умолчанию


class Settings(BaseSettings):
    bot: BotSettings
    logging: LoggingSettings = LoggingSettings()
    yookassa: YooKassaSettings
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file="config/.env",  # Путь до .env (относительно исполняемого файла)
        env_nested_delimiter="__",  # Для вложенных настроек
        extra="ignore"
    )


# Глобальный экземпляр
settings = Settings()
# print(settings.logging.level)
# print(settings.debug)
# print(settings.bot.token.get_secret_value())
# print(settings.bot.parse_mode)
# print(settings.yookassa.secret.get_secret_value())