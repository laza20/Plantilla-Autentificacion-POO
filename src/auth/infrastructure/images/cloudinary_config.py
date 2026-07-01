import cloudinary
import cloudinary.uploader
from src.config.config import settings 

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

cloudinary_uploader = cloudinary.uploader