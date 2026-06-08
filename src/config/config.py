from pydantic_settings import BaseSettings, SettingsConfigForm

class Settings(BaseSettings):
    #General settings
    is_prod: bool = False
    DATABASE_URL: str
    
    #JWT settings
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    #Mail settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool

    #App settings
    NOMBRE_APP: str
    BASE_URL: str
    
    #Cloudinary settings
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_UPLOAD_PRESET: str

    model_config = SettingsConfigForm(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()