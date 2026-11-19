from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #General settings
    is_prod: bool = False
    DATABASE_URL: str
    
    #JWT settings
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_DURATION: int
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int
    VERIFY_MAIL_RECUPERACION: int
    EXPIRACION_MAIL_RECUPERACION : int
    
    #Mail settings

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True

    #App settings
    NOMBRE_APP: str
    BASE_URL: str
    ELIMINACION_CUENTA:int
    REACTIVACION_CUENTA:int
    
    #Cloudinary settings
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_UPLOAD_PRESET: str

    RATE_LIMITER_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()


def get_settings() -> Settings:
    return settings