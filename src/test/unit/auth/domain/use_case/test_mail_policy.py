import pytest
from src.auth.domain.exceptions.domain import MailNoValido
from src.auth.domain.services.mail_policy import MailPolicyService


def test_debe_dar_error_por_mail_corto():
    """
    Verifica que el correo no es válido por ser demasiado corto.
    """
    service = MailPolicyService()
    with pytest.raises(MailNoValido):
        service.validar("a@b.c")


def test_debe_verificar_que_falla_si_no_tiene_arroba():
    """
    Verifica que el correo no es válido por no tener el símbolo '@'.
    """
    service = MailPolicyService()
    with pytest.raises(MailNoValido):
        service.validar("correo_sin_arroba.com")