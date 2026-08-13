from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Microservice IA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Sécurité : Évite un crash si le .env est ignoré par Git
    MODEL_NAME: str = "yangy50/garbage-classification" 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )



settings = Settings()