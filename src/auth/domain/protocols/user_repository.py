from typing import Protocol, runtime_checkable
from src.auth.models import AuthUser

@runtime_checkable
class UserRepositoryProtocol(Protocol):
    """
    Contrato para repositorios de usuarios.
    
    ¿Qué es?
    --------
    Define la interfaz que CUALQUIER sistema de persistencia de usuarios debe cumplir.
    Puede ser SQL (PostgreSQL, MySQL), NoSQL (MongoDB), Cloud (Firebase), etc.
    
    ¿Cómo implementar?
    ------------------
    1. Crea una clase que implemente estos cinco métodos
    2. Cada método debe manejar un aspecto diferente del usuario
    3. Registra la clase en dependencies.py
    
    Ejemplo de implementación (SQLModel):
    
    from sqlmodel import Session, select
    
    class UserRepository:
        def __init__(self, session: Session):
            self.session = session
        
        def insertar(self, usuario: AuthUser) -> AuthUser:
            self.session.add(usuario)
            self.session.commit()
            self.session.refresh(usuario)
            return usuario
        
        def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
            statement = select(AuthUser).where(AuthUser.id_usuario == id_usuario)
            return self.session.exec(statement).first()
        
        # ... resto de métodos
    
    Atributos requeridos:
    --------------------
    Ninguno. Solo implementa los métodos.
    
    Métodos requeridos:
    -------------------
    """
    
    def insertar(self, usuario: AuthUser) -> AuthUser:
        """
        Inserta un nuevo usuario en la base de datos.
        
        Parámetros:
        -----------
        usuario : AuthUser
            Objeto del usuario a insertar.
            Debe tener al menos:
            - email: Dirección de correo (único)
            - password: Hash de la contraseña
            - nombre: Nombre del usuario
            
            Típicamente NO tiene:
            - id_usuario: Se genera automáticamente (autoincrement)
            - is_verified: Se pone False por defecto
            - estado: Se pone PENDIENTE o similar
        
        Retorna:
        --------
        AuthUser
            El mismo usuario pero con:
            - id_usuario: Asignado por la BD (autoincrement)
            - is_verified: False (no verificado)
            - estado: Probablemente PENDIENTE
            - timestamps: created_at, updated_at si existen
        
        Excepciones esperadas:
        ----------------------
        IntegrityError (o equivalente)
            Si el email ya existe (violaría unique constraint)
        
        Exception
            Si hay error de conexión BD, validación, etc.
        
        Ejemplo práctico:
        -----------------
        # En AuthService.register()
        usuario = AuthUser(
            email="juan@example.com",
            password="$argon2id$v=19$...",  # Hash
            nombre="Juan"
        )
        # usuario.id_usuario = None (aún no existe)
        
        usuario_creado = self.user_repository.insertar(usuario)
        
        # Ahora:
        print(usuario_creado.id_usuario)  # 1
        print(usuario_creado.is_verified)  # False
        print(usuario_creado.estado)  # PENDIENTE
        
        Notas de implementación:
        -----------------------
        - El usuario es nuevo (no debe existir)
        - Email debe ser único (validación BD)
        - Password debe estar hasheado ANTES de insertar
        - Los campos id_usuario, is_verified, estado se asignan por defecto
        - Debe persistir en BD (commit/flush)
        - Retorna el objeto actualizado con ID asignado
        - Si el email ya existe, lanza excepción (no silenciosamente)
        """
        ...
    
    def obtener_por_id_sin_activar(self, id_usuario: int) -> AuthUser | None:
        """
        Obtiene un usuario por ID SIN importar su estado (incluso si no está verificado).
        
        Parámetros:
        -----------
        id_usuario : int
            ID único del usuario en la BD.
            Ejemplo: 1, 2, 3, ...
        
        Retorna:
        --------
        AuthUser | None
            El usuario si existe.
            None si no existe.
            
            Características:
            - Se retorna incluso si is_verified = False
            - Se retorna incluso si estado != ACTIVO
            - Objeto completo con todos los campos
        
        Excepciones esperadas:
        ----------------------
        Ninguna. Retorna None si no existe (no lanza).
        
        Ejemplo práctico:
        -----------------
        # En AuthService.verificar_mail()
        user_id_db = self.token_service.get_user_id_from_access_token(token)
        # user_id_db = 1
        
        usuario = self.user_repository.obtener_por_id_sin_activar(user_id_db)
        # usuario = AuthUser(id_usuario=1, email="...", is_verified=False, ...)
        
        if usuario is None:
            raise ValueError("Usuario no encontrado")
        
        # Ahora lo activas
        usuario = self.user_repository.activar(usuario)
        
        Caso de uso específico:
        -----------------------
        Este método es ESPECIAL porque:
        - El usuario se registró hace poco (is_verified = False)
        - El usuario aún NO está ACTIVO
        - Pero necesitas buscarlo para verificar su email
        - Los métodos obtener_por_email, obtener_por_id buscan solo ACTIVOS
        
        Notas de implementación:
        -----------------------
        - No filtra por is_verified o estado
        - Búsqueda por ID único (siempre retorna 0 o 1 resultado)
        - Si no existe, retorna None (no lanza excepción)
        - Útil para estados transitorios (verificación pendiente)
        """
        ...
    
    def activar(self, usuario: AuthUser) -> AuthUser:
        """
        Activa/verifica un usuario (marca como email verificado y activo).
        
        Parámetros:
        -----------
        usuario : AuthUser
            Usuario a activar.
            Típicamente obtenido de obtener_por_id_sin_activar().
            
            Debe tener:
            - id_usuario: ID válido
            - is_verified: Actualmente False
            - estado: Actualmente PENDIENTE o similar
        
        Retorna:
        --------
        AuthUser
            El mismo usuario pero MODIFICADO:
            - is_verified = True
            - estado = ACTIVO
            - Cambios persistidos en BD
        
        Excepciones esperadas:
        ----------------------
        Exception
            Si hay error al actualizar BD
        
        Ejemplo práctico:
        -----------------
        # En AuthService.verificar_mail()
        usuario = self.user_repository.obtener_por_id_sin_activar(user_id)
        # usuario.is_verified = False
        # usuario.estado = PENDIENTE
        
        usuario_activado = self.user_repository.activar(usuario)
        
        # Ahora:
        print(usuario_activado.is_verified)  # True
        print(usuario_activado.estado)  # ACTIVO
        
        Ciclo de vida del usuario:
        ---------------------------
        1. Registro: insertar() → usuario PENDIENTE, no verificado
        2. Email enviado: Usuario recibe link con token
        3. Click link: GET /usuarios/verificar/{token}
        4. Backend: obtener_por_id_sin_activar() + activar()
        5. Resultado: Usuario ACTIVO, verificado
        6. Usuario puede hacer login (obtener_por_email solo retorna ACTIVOS)
        
        Notas de implementación:
        -----------------------
        - Cambios al menos dos campos: is_verified + estado
        - Debe persistir cambios en BD (commit/flush)
        - Retorna el objeto actualizado
        - Solo se llama después de verificar email (no en otros lugares)
        - Transición irreversible (el usuario no vuelve a PENDIENTE)
        """
        ...
    
    def obtener_por_email(self, email: str) -> AuthUser | None:
        """
        Obtiene un usuario ACTIVO por su email.
        
        Parámetros:
        -----------
        email : str
            Dirección de correo del usuario.
            Búsqueda case-sensitive (típicamente).
            Ejemplo: "juan@example.com"
        
        Retorna:
        --------
        AuthUser | None
            El usuario si:
            - Existe en BD
            - Email coincide exactamente
            - is_verified = True
            - estado = ACTIVO
            
            None si no encuentra o no está activo.
        
        Excepciones esperadas:
        ----------------------
        Ninguna. Retorna None si no existe.
        
        Ejemplo práctico:
        -----------------
        # En AuthService.login()
        email = "juan@example.com"
        password = "MiContraseña123!"
        
        usuario_db = self.user_repository.obtener_por_email(email)
        # usuario_db = AuthUser(...) si existe y está ACTIVO
        # usuario_db = None si no existe o no está verificado
        
        if usuario_db is None:
            raise LoginError("Usuario o contraseña incorrectos")
        
        # Verificar contraseña
        if not self.password_service.verify_password(password, usuario_db.password):
            raise LoginError("Usuario o contraseña incorrectos")
        
        Diferencia vs obtener_por_id_sin_activar:
        -------------------------------------------
        | Método | Búsqueda | Filtra activos | Caso de uso |
        |--------|----------|----------------|------------|
        | obtener_por_email | email | SÍ (solo ACTIVOS) | Login |
        | obtener_por_id_sin_activar | ID | NO | Verificación email |
        
        Notas de implementación:
        -----------------------
        - Filtro por estado = ACTIVO (NO retorna PENDIENTES)
        - Filtro por is_verified = True
        - Email debe ser único (solo 0 o 1 resultado)
        - Si no existe o no está activo, retorna None
        - No lanza excepción (retorna None es seguro)
        - Este método es el que usa login
        """
        ...
    
    def obtener_por_id(self, id_usuario: int) -> AuthUser | None:
        """
        Obtiene un usuario ACTIVO por su ID.
        
        Parámetros:
        -----------
        id_usuario : int
            ID único del usuario.
            Ejemplo: 1, 2, 3, ...
        
        Retorna:
        --------
        AuthUser | None
            El usuario si:
            - Existe en BD
            - estado = ACTIVO
            - is_verified = True
            
            None si no existe o no está activo.
        
        Excepciones esperadas:
        ----------------------
        Ninguna. Retorna None si no existe.
        
        Ejemplo práctico:
        -----------------
        # En un endpoint autenticado
        @router.get("/usuarios/me")
        async def get_me(
            current_user: AuthUser = Depends(get_current_user)
        ):
            usuario = auth_service.get_user(current_user)
            # Internamente: self.user_repository.obtener_por_id(current_user.id_usuario)
            return usuario
        
        Flujo típico:
        ---------------
        1. Usuario hace login → obtener_por_email()
        2. Backend genera tokens
        3. Usuario usa token en Authorization header
        4. Backend extrae user_id del token
        5. Backend llama obtener_por_id(user_id) para obtener datos actuales
        6. Retorna usuario ACTIVO
        
        Notas de implementación:
        -----------------------
        - Filtro por id_usuario = valor
        - Filtro por estado = ACTIVO
        - Filtro por is_verified = True
        - Si no existe o no está activo, retorna None
        - Similar a obtener_por_email pero búsqueda es por ID
        - Este método se llama en endpoints autenticados para obtener datos del usuario
        """
        ...