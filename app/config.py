from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mensagens Automaticas"
    database_url: str = "mysql+pymysql://root:root@localhost:3306/mensagens_automaticas"
    secret_key: str = "troque-esta-chave-em-producao"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
