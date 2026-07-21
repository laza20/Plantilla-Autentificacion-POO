from src.auth.domain.exceptions.domain import ContraseñaNoSegura

class StubPasswordPolicy:
    def __init__(self):
        self.es_valida = True

    def validar(self, password: str) -> None:
        """
        Función para simular la validación de una contraseña.
        """
        if not self.es_valida:
            raise ContraseñaNoSegura()
        