from src.exceptions.domain import ContraseñaNoSegura
import re

class PasswordPolicyService:

    def validar(self, contraseña: str) -> None:
        """
        Valida que la contraseña cumpla con los requisitos de seguridad.
        Requisitos:
        - Al menos 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un carácter especial
        """

        if len(contraseña) < 8:
            raise ContraseñaNoSegura()
        if not re.search(r'[A-Z]', contraseña):
            raise ContraseñaNoSegura()
        if not re.search(r'[a-z]', contraseña):
            raise ContraseñaNoSegura()
        if not re.search(r'[0-9]', contraseña):
            raise ContraseñaNoSegura()
        if not re.search(r'[^a-zA-Z0-9]', contraseña):
            raise ContraseñaNoSegura()
