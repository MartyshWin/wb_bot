from pathlib import Path
from pydantic import BaseModel, Field, SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

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

class DatabaseSettings(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    #noinspection PyDataclass
    naming_convention: dict[str, str] = Field(
        default_factory=lambda: {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class YooKassaSettings(BaseModel):
    shop_id: str                     # ID магазина в ЮKassa
    secret: SecretStr                # Секретный ключ
    currency: str = "RUB"            # Валюта по‑умолчанию


class Settings(BaseSettings):
    bot: BotSettings
    logging: LoggingSettings = LoggingSettings()
    db: DatabaseSettings
    yookassa: YooKassaSettings
    debug: bool = False

    # MAJOR.MINOR.PATCH
    version: str = "0.0.1"

    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env"
        ),  # Путь до .env (относительно исполняемого файла)
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