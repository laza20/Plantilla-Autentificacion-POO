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

def test_debe_verificar_que_falla_si_no_tiene_punto():
    """
    Verifica que el correo no es válido por no tener un punto.
    """
    service = MailPolicyService()
    with pytest.raises(MailNoValido):
        service.validar("correo@sinpunto")

def test_debe_dar_error_si_el_correo_no_contiene_caracteres_luego_del_punto():
    """
    Verifica que el correo no es válido si no tiene caracteres después del punto.
    """
    service = MailPolicyService()
    with pytest.raises(MailNoValido):
        service.validar("correo@dominio.")


def test_debe_dar_error_si_el_mail_no_tiene_caracteres_antes_del_arroba():
    """
    Verifica que el correo no es válido si no tiene caracteres antes del símbolo '@'.
    """
    service = MailPolicyService()
    with pytest.raises(MailNoValido):
        service.validar("@dominio.com")


def test_debe_dar_error_si_el_mail_no_tiene_caracteres_entre_arroba_y_punto():
    """
    Verifica que el correo no es válido si no tiene caracteres entre el símbolo '@' y el punto.
    """
    service = MailPolicyService()
    with pytest.raises(MailNoValido):
        service.validar("correo@.com")