from src.auth.domain.exceptions.domain import MailNoValido

class StubMailPolicy:
    def __init__(self):
        self.es_valido = True

    def validar(self, mail: str) -> None:
        """
        Función para simular la validación de un correo electrónico.
        """
        if not self.es_valido:
            raise MailNoValido()
        