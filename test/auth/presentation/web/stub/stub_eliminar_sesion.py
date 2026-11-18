


class StubEliminarSesionesUseCase:
    def __init__(self):
        self.resultado_a_devolver = None
        self.excepcion_a_lanzar = None

    def ejecutar(self, id_sesion, id_usuario):
        if self.excepcion_a_lanzar:
            raise self.excepcion_a_lanzar
        return self.resultado_a_devolver