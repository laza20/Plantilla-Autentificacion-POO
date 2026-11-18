def crear_override(stub_class, *, resultado=None, excepcion=None):
    def override():
        stub = stub_class()
        stub.resultado_a_devolver = resultado
        stub.excepcion_a_lanzar = excepcion
        return stub
    return override