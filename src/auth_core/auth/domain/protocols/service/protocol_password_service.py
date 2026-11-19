from typing import Protocol, runtime_checkable


@runtime_checkable
class PasswordProtocol(Protocol):
    """
    Contrato para servicios de hashing y verificación de contraseñas.

    Define la interfaz que cualquier servicio de contraseñas debe cumplir
    (Argon2, Bcrypt, PBKDF2, Scrypt, etc.).

    Cómo implementar:
        1. Crear una clase con los dos métodos de este contrato, respetando las firmas.
        2. Registrarla en dependencies.py.

    Ejemplo (Argon2 con pwdlib):

        from pwdlib import PasswordHash

        class PasswordService:
            def __init__(self):
                self.pwd_context = PasswordHash.recommended()

            def hash_password(self, password: str) -> str:
                return self.pwd_context.hash(password)

            def verify_password(self, plain: str, hashed: str) -> bool:
                return self.pwd_context.verify(plain, hashed)

    Atributos requeridos: ninguno.
    """

    def hash_password(self, password: str) -> str:
        """
        Genera el hash de una contraseña en texto plano.

        Args:
            password: Contraseña en texto plano ingresada por el usuario.

        Returns:
            Hash codificado de la contraseña, apto para persistir en la BD.
            - Irreversible: no permite recuperar la contraseña original.
            - No determinístico: incluye un salt aleatorio, por lo que hashear
              dos veces la misma contraseña produce hashes distintos.
            - Incluye en la propia cadena el algoritmo, los parámetros y el salt
              (ej. Argon2: "$argon2id$v=19$m=65540,t=2,p=1$...").

        Notas:
            - Nunca persistir la contraseña en texto plano; solo el hash.
            - Usar un algoritmo moderno (Argon2 > Bcrypt > PBKDF2).

        Ejemplo en AuthService.register():
            objeto_usuario.password = self.password_service.hash_password(
                objeto_usuario.password
            )
        """
        ...

    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verifica si una contraseña en texto plano coincide con un hash almacenado.

        Args:
            plain: Contraseña en texto plano ingresada por el usuario (login).
            hashed: Hash almacenado en la BD, generado con hash_password().

        Returns:
            True si coinciden, False si la contraseña es incorrecta.
            Una contraseña incorrecta nunca lanza excepción: devuelve False.

        Notas:
            - La comparación la realiza el algoritmo de hashing (tiempo constante);
              nunca comparar hashes con ==.
            - El hash debe haber sido generado con un algoritmo compatible
              con la implementación.

        Ejemplo en AuthService.login():
            es_valido = self.password_service.verify_password(
                plain=password,
                hashed=usuario_db.password,
            )
            if not es_valido:
                raise LoginError("Usuario o contraseña incorrectos")
        """
        ...