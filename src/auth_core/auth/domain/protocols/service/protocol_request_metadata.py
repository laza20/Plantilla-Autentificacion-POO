from typing import Protocol

class RequestMetadataProtocol(Protocol):
    """Contrato para extraer metadata de red de la request HTTP entrante.

    Desacopla a los casos de uso (ej. registro de sesión) de la forma
    concreta en que se obtienen IP y user agent, siguiendo el mismo
    criterio de Protocol que el resto de las dependencias del sistema.
    """

    def get_ip(self) -> str:
        """Devuelve la IP del cliente que originó la request."""
        ...

    def get_user_agent(self) -> str:
        """Devuelve el user agent del cliente que originó la request."""
        ...