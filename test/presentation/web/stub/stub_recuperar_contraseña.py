


class StubRecuperarContraseñaUseCase:
    def __init__(self):
        self.resultado_a_devolver = None
        self.excepcion_a_lanzar = None

    def ejecutar(self, id_usuario:int, nueva_contraseña:str):
        if self.excepcion_a_lanzar:
            raise self.excepcion_a_lanzar
        return self.resultado_a_devolver
    

    def decode_token(self, token:str):
        if self.excepcion_a_lanzar:
            raise self.excepcion_a_lanzar
        return {"sub": 1, "type": "reset", "exp": 9999999999}