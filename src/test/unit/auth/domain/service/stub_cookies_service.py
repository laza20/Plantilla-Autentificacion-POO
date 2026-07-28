class StubCookiesService:

    def __init__(self):
        self.fue_llamado = False
        self.response = None
        self.access_token = None
        self.refresh_token = None

    def set_auth_cookies(
        self,
        response,
        access_token: str,
        refresh_token: str
    ):
        self.fue_llamado = True
        self.response = response
        self.access_token = access_token
        self.refresh_token = refresh_token


    def delete_auth_cookies(self, response):
        self.fue_llamado = True
        self.response = response