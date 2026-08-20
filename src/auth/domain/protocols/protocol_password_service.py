from typing import Protocol, runtime_checkable

@runtime_checkable
class PasswordProtocol(Protocol):
    """
    Contrato para servicios de hashing y verificación de contraseñas.
    
    ¿Qué es?
    --------
    Define la interfaz que CUALQUIER servicio de contraseñas debe cumplir.
    Puede ser Argon2, Bcrypt, PBKDF2, Scrypt, etc.
    
    ¿Cómo implementar?
    ------------------
    1. Crea una clase que implemente estos dos métodos
    2. Asegúrate de cumplir exactamente las firmas
    3. Registra la clase en dependencies.py
    
    Ejemplo de implementación (Argon2):
    
    from pwdlib import PasswordHash
    
    class PasswordService:
        def __init__(self, settings: Settings):
            self.settings = settings
            self.pwd_context = PasswordHash.recommended()
        
        def hash_password(self, password: str) -> str:
            # Hash usando Argon2
            return self.pwd_context.hash(password)
        
        def verify_password(self, plain: str, hashed: str) -> bool:
            # Verifica contraseña usando Argon2
            return self.pwd_context.verify(plain, hashed)
    
    Atributos requeridos:
    --------------------
    Ninguno. Solo implementa los métodos.
    
    Métodos requeridos:
    -------------------
    """
    
    def hash_password(self, password: str) -> str:
        """
        Genera un hash seguro de una contraseña en texto plano.
        
        Parámetros:
        -----------
        password : str
            Contraseña en texto plano proporcionada por el usuario.
            Ejemplo: "MiContraseña123!"
            
            Nota: Esta contraseña está en memoria.
            Tu implementación debe hashearla de forma segura
            para que no se pueda recuperar el original.
        
        Retorna:
        --------
        str
            Hash de la contraseña (cadena codificada).
            
            Características:
            - No reversible (no se puede extraer el password original)
            - Determinístico pero con salt (cada hash es diferente)
            - Largo típico: 60-100+ caracteres según algoritmo
            
            Ejemplos por algoritmo:
            
            Argon2:  "$argon2id$v=19$m=65540,t=2,p=1$..."
            Bcrypt:  "$2b$12$r9h..." (60 caracteres fijos)
            PBKDF2:  "pbkdf2_sha256$260000$..." (variable)
        
        Excepciones esperadas:
        ----------------------
        Exception (genérica)
            Si hay error durante el hashing (raro en caso normal)
        
        Ejemplo práctico:
        -----------------
        >>> password_service = PasswordService(settings)
        >>> plain_password = "MiContraseña123!"
        >>> hashed = password_service.hash_password(plain_password)
        >>> print(type(hashed))
        <class 'str'>
        >>> print(len(hashed))
        97  # Longitud del hash Argon2
        
        Notas de implementación:
        -----------------------
        - NUNCA almacenes el password en texto plano
        - El hash debe ser impredecible (usa salt automático)
        - Usa un algoritmo moderno (Argon2 > Bcrypt > PBKDF2)
        - El hash es lo que guardas en la BD
        - El password original se descarta después de hashear
        
        Flujo en AuthService:
        --------------------
        # En AuthService.register()
        objeto_usuario.password = "MiContraseña123!"
        
        # Hashear antes de guardar
        objeto_usuario.password = self.password_service.hash_password(
            objeto_usuario.password
        )
        # Ahora objeto_usuario.password = "$argon2id$v=19$..."
        
        # Guardar en BD (el password ya es un hash)
        usuario_creado = self.auth_user_repository.insertar(objeto_usuario)
        # En BD se almacena el hash, nunca el password original
        """
        ...
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verifica si un password en texto plano coincide con su hash almacenado.
        
        Parámetros:
        -----------
        plain : str
            Contraseña en texto plano proporcionada por el usuario (en login).
            Ejemplo: "MiContraseña123!"
            
            Nota: El usuario la proporciona, la comparas contra el hash en BD.
        
        hashed : str
            Hash almacenado en la base de datos.
            Ejemplo: "$argon2id$v=19$m=65540,t=2,p=1$..."
            
            Este es el valor que guardaste cuando el usuario se registró.
        
        Retorna:
        --------
        bool
            True si el password coincide con el hash.
            False si no coincide (usuario ingresó contraseña incorrecta).
            
            Importante: Este método NUNCA falla, siempre retorna bool.
                       No lanza excepción si la contraseña es incorrecta.
        
        Excepciones esperadas:
        ----------------------
        Exception (muy raro)
            Si el hash está malformado o corrupto (casi nunca pasa)
        
        Ejemplo práctico:
        -----------------
        # Scenario: Login de usuario
        
        >>> password_service = PasswordService(settings)
        >>> usuario_db_password = "$argon2id$v=19$..."  # Hash en BD
        
        # Usuario ingresa contraseña en login
        >>> usuario_input = "MiContraseña123!"
        
        # Verificas
        >>> es_correcto = password_service.verify_password(
        ...     plain=usuario_input,
        ...     hashed=usuario_db_password
        ... )
        >>> print(es_correcto)
        True  # Contraseña correcta
        
        # Si el usuario ingresa mal:
        >>> usuario_input_incorrecto = "ContraseñaWrong!"
        >>> es_correcto = password_service.verify_password(
        ...     plain=usuario_input_incorrecto,
        ...     hashed=usuario_db_password
        ... )
        >>> print(es_correcto)
        False  # Contraseña incorrecta
        
        Notas de implementación:
        -----------------------
        - El plain password viene del request (login)
        - El hashed password viene de BD
        - Comparación tiempo-constante (previene timing attacks)
        - NUNCA compares strings directamente (== es inseguro)
        - El algoritmo debe ser el mismo que usaste para hashear
        
        Flujo en AuthService:
        --------------------
        # En AuthService.login()
        usuario_db = self.auth_user_repository.obtener_por_email(email)
        
        # usuario_db.password es el hash en BD
        # password es lo que ingresó el usuario
        
        es_valido = self.password_service.verify_password(
            plain=password,
            hashed=usuario_db.password
        )
        
        if es_valido:
            # Login exitoso
            tokens = self._crear_tokens_usuario(usuario_db.id_usuario)
        else:
            # Contraseña incorrecta
            raise LoginError("Usuario o contraseña incorrectos")
        """
        ...
