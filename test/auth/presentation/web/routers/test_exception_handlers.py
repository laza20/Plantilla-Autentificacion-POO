from src.auth_core.auth.presentation.web.exception_handlers import HTTP_STATUS_BY_EXCEPTION, obtener_status_code
from src.auth_core.auth.domain.exceptions.usuarios_exceptions import UsuarioError
from src.auth_core.domain.exceptions.domain import DomainError



def obtener_subclases(clase):
    for sub in clase.__subclasses__():
        if sub.__module__.startswith("auth_core.") and ".test." not in sub.__module__:
            yield sub
        yield from obtener_subclases(sub)


def test_subclase_sin_entrada_propia_hereda_el_status_del_padre():
    class NuevoErrorDeUsuario(UsuarioError):
        pass

    assert obtener_status_code(NuevoErrorDeUsuario()) == 400


def test_todas_las_excepciones_tienen_status_explicito():
    sin_status = sorted(
        exc.__name__ for exc in set(obtener_subclases(DomainError))
        if exc not in HTTP_STATUS_BY_EXCEPTION
    )
    assert not sin_status, f"Excepciones sin status HTTP: {sin_status}"