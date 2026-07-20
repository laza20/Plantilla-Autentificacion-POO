import pytest
from src.auth.domain.exceptions.domain import ContraseñaNoSegura
from src.auth.domain.services.password_policy import PasswordPolicyService


def test_debe_dar_error_por_contraseña_sin_numeros():
    """
    Verifica que la contraseña no cumple con la política de seguridad al no contener números.
    """
    service = PasswordPolicyService()
    with pytest.raises(ContraseñaNoSegura):
        service.validar("Password@asasa")


def test_debe_dar_error_por_contraseña_sin_mayusculas():
    """
    Verifica que la contraseña no cumple con la política de seguridad al no contener mayusculas.
    """
    service = PasswordPolicyService()

    with pytest.raises(ContraseñaNoSegura):
        service.validar("password@asasa123")

def test_debe_dar_error_por_contraseña_sin_minusculas():
    """
    Verifica que la contraseña no cumple con la política de seguridad al no contener minusculas.
    """
    service = PasswordPolicyService()
    with pytest.raises(ContraseñaNoSegura):
        service.validar("PASSWORD@ASASA123")

def test_debe_dar_error_por_contraseña_sin_caracter_especial():
    """
    Verifica que la contraseña no cumple con la política de seguridad al no contener caracter especial.
    """
    service = PasswordPolicyService()
    with pytest.raises(ContraseñaNoSegura):
        service.validar("PASSWORDASASA123")

