from typing import Protocol


class AuthMailContentProtocol(Protocol):
    """
    Contrato para la generación del contenido (HTML) de los correos de autenticación.

    Cada método recibe la URL de acción y el nombre del proyecto, y devuelve
    el cuerpo del correo ya renderizado. El envío del correo NO es responsabilidad
    de este contrato: solo produce el contenido.

    Cómo implementar:
        1. Crear una clase con los cuatro métodos de este contrato.
        2. Registrarla en dependencies.py.

    Parámetros comunes:
        url: Enlace que el usuario debe abrir (incluye el token del flujo).
        nombre_proyecto: Nombre de la aplicación que se muestra en el correo.

    Retorno común:
        str con el HTML del correo.
    """

    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Genera el correo de verificación de cuenta.

        Se envía al registrarse (o al reenviar el correo de activación).
        La url debe contener el token creado con create_verificacion_token().
        """
        ...

    def generar_correo_recuperacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Genera el correo de recuperación de contraseña.

        La url debe contener el token plano del flujo de recuperación,
        generado con generar_token_plano().
        """
        ...

    def generar_correo_eliminacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Genera el correo de confirmación de baja de cuenta.

        La url debe contener el token creado con create_eliminacion_token().
        """
        ...

    def generar_correo_reactivacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Genera el correo de reactivación de una cuenta dada de baja.

        La url debe contener el token creado con create_reactivacion_token().
        """
        ...