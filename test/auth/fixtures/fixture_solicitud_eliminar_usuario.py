from test.auth.unit.auth.domain.service import stub_auth_mail_content, stub_mail_service
from test.auth.unit.auth.domain.service import (stub_token_service)
from test.auth.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from auth_core.auth.application.use_cases.eliminar_usuario.solicitud_eliminar_usuario import SolicitudEliminacionUsuarioUseCase
from test.config.config import TestSettings
from test.auth.unit.auth.domain.service import (stub_mail_policy_service)


class SolicitudEliminacionUsuarioTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.mail_content = stub_auth_mail_content.StubAuthMailContent()
        self.token_service = stub_token_service.StubTokenService()
        self.base_de_datos_url = TestSettings().BASE_URL
        self.nombre_app = TestSettings().NOMBRE_APP

    def use_case(self):
        return SolicitudEliminacionUsuarioUseCase(
            auth_user_repository=self.auth_user_repository,
            mail_service=self.mail_service,
            mail_content=self.mail_content,
            token_service=self.token_service,
            base_de_datos_url=self.base_de_datos_url,
            nombre_app=self.nombre_app
        )