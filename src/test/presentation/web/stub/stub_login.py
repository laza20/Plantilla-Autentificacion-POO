


class StubLoginUseCase:
    def __init__(self):
        self.resultado_a_devolver = None
        self.excepcion_a_lanzar = None

    def ejecutar(self, email, password, ip, user_agent, response):
        if self.excepcion_a_lanzar:
            raise self.excepcion_a_lanzar
        return self.resultado_a_devolver