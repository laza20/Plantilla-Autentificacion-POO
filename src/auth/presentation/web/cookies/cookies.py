from src.config.config import Settings
from fastapi import Response


class CookiesService:
    def __init__(self, settings: Settings):
        self.settings = settings


    def get_cookie_settings(self):
        is_prod = self.settings.is_prod
        cookie_settings = {
                "httponly": True,
                "secure": is_prod,    
                "samesite": "none" if is_prod else "lax",
                "path": "/",
            }
        return cookie_settings
    

    def set_auth_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str
    ):

        params = self.get_cookie_settings()

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=15 * 60,
            **params
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=7 * 24 * 60 * 60,
            **params
        )

    def set_access_cookie(
        self,
        response: Response,
        access_token: str
    ):

        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=15 * 60,
            **self.get_cookie_settings()
        )
    
    def delete_auth_cookies(
        self,
        response: Response
    ):

        params = self.get_delete_cookie_settings()

        response.delete_cookie("access_token", **params)
        response.delete_cookie("refresh_token", **params)

    def get_delete_cookie_settings(self):

        return {
            "path": "/",
            "httponly": True,
            "secure": self.settings.is_prod,
            "samesite": "none" if self.settings.is_prod else "lax"
        }


    def set_reset_cookie(self, reset_token:str, response:Response, url:str):
        max_age = self.settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES * 60

        response.set_cookie(
            key="reset_token",
            value=reset_token,
            max_age=max_age,
            httponly=True,
            secure=self.settings.is_prod,
            samesite="none" if self.settings.is_prod else "lax",
            path=url
        )