from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str
    TEST_DB_NAME: str
    INVOICE_LANG: str = "en"
    
    DOCS_URL: str = "/docs"
    TOKEN_URL: str = "/users/login"

    ACCESS_TOKEN_EXPIRATION_SECONDS: int = 60 * 15
    REFRESH_TOKEN_EXPIRATION_SECONDS: int = 60 * 60 * 24 * 7
    ACCESS_TOKEN_ALGORITHM: str = "RS256"
    REFRESH_TOKEN_ALGORITHM: str = "HS256"
    REFRESH_TOKEN_SECRET_KEY: str
    PUBLIC_KEY_PATH: str = "public_key.pem"
    PRIVATE_KEY_PATH: str = "private_key.pem"
    TOKEN_EXCLUDE: list[str] = ["/users/login/", "/users/token/refresh/", "/users/create/", DOCS_URL, "/openapi.json", "/redoc", TOKEN_URL]
    
    EMAIL_NAME: str
    EMAIL_PASSWORD: str
    EMAIL_SERVER: str
    EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECONDS: int = 60 * 60 * 24 * 7

@lru_cache(maxsize=1)
def get_settings():
    return Settings() # type: ignore

settings = get_settings()
