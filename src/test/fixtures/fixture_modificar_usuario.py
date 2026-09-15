from src.test.unit.auth.domain.service import (
    stub_image_service,
    stub_mail_service,
    stub_token_service,
    stub_unit_of_work
)
from src.test.unit.auth.domain.fakes.fake_auth_user_repository import FakeUserRepository
from src.auth.application.use_cases.modificar_usuario import ModificarUsuarioUseCase
from src.test.config.config import TestSettings
from src.test.unit.auth.domain.service import stub_mail_policy_service


class ModificarUsuarioTestEnvironment:

    def __init__(self):
        self.auth_user_repository = FakeUserRepository()
        self.mail_service = stub_mail_service.StubMailService()
        self.image_service = stub_image_service.StubImageService()
        self.token_service = stub_token_service.StubTokenService()
        self.mail_policy = stub_mail_policy_service.StubMailPolicy()
        self.settings = TestSettings()
        self.unit_of_work_service = stub_unit_of_work.StubUnitOfWork()

    def use_case(self):
        return ModificarUsuarioUseCase(
            auth_user_repository=self.auth_user_repository,
            mail_service=self.mail_service,
            image_service=self.image_service,
            token_service=self.token_service,
            mail_policy=self.mail_policy,
            settings=self.settings,
            unit_of_work_service=self.unit_of_work_service
        )