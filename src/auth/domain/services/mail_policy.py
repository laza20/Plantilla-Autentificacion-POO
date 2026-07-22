from src.auth.domain.exceptions.domain import MailNoValido
import re

class MailPolicyService:

    def validar(self, mail: str) -> None:
        """
        Valida que el mail cumpla con los requisitos de seguridad.
        Requisitos:
        - debe tener un solo arroba.
        - debe tener un punto luego del arroba.
        - debe tener una separacion por caracteres entre el punto y el arroba.
        - debe tener al menos 6 caracteres.
        """

        if len(mail) < 6:
            raise MailNoValido()
        if not re.findall(r'^[^@]+@[^@]+\.[^@]+$', mail):
            raise MailNoValido()
