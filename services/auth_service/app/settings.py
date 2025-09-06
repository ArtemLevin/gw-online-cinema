from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cinema:cinema@db:5432/auth_db"
    redis_host: str = "redis"
    redis_port: int = 6379
    jwt_secret: str = "supersecretjwt"
    jwt_alg: str = "HS256"
    access_token_expires_min: int = 30
    refresh_token_expires_min: int = 43200

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False

settings = Settings()
