from test.auth.unit.auth.domain.service import stub_auth_mail_content, stub_image_service, stub_mail_service, stub_token_service
from test.auth.unit.auth.domain.service import (
    stub_unit_of_work
)
from test.auth.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from auth_core.auth.application.use_cases.modificar_usuario import ModificarUsuarioUseCase
from test.config.config import TestSettings
from test.auth.unit.auth.domain.service import stub_mail_policy_service


class ModificarUsuarioTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.image_service = stub_image_service.StubImageService()
        self.mail_content = stub_auth_mail_content.StubAuthMailContent()
        self.token_service = stub_token_service.StubTokenService()
        self.mail_policy = stub_mail_policy_service.StubMailPolicy()
        self.base_de_datos_url = TestSettings().BASE_URL
        self.nombre_app = TestSettings().NOMBRE_APP
        self.unit_of_work_service = stub_unit_of_work.StubUnitOfWork()

    def use_case(self):
        return ModificarUsuarioUseCase(
            auth_user_repository=self.auth_user_repository,
            mail_service=self.mail_service,
            mail_content = self.mail_content,
            image_service=self.image_service,
            token_service=self.token_service,
            mail_policy=self.mail_policy,
            base_de_datos_url=self.base_de_datos_url,
            nombre_app=self.nombre_app,
            unit_of_work_service=self.unit_of_work_service
        )