from src.auth.infrastructure.persistence.postgres.models_auth_users import UserTokens


class StubVerifyMailUseCase:
    def __init__(self):
        self.resultado_a_devolver = None
        self.excepcion_a_lanzar = None

    def ejecutar(self, token):
        if self.excepcion_a_lanzar:
            raise self.excepcion_a_lanzar
        self.resultado_a_devolver = UserTokens(
            access_token = "access_token_1",
            refresh_token = "refresh_token_1"
        )

        return self.resultado_a_devolver