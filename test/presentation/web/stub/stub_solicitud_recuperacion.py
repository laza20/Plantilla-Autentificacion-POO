


class StubSolicitudRecuperacionUseCase:
    def __init__(self):
        self.resultado_a_devolver = None
        self.excepcion_a_lanzar = None

    async def ejecutar(self, email):
        if self.excepcion_a_lanzar:
            raise self.excepcion_a_lanzar
        return self.resultado_a_devolver