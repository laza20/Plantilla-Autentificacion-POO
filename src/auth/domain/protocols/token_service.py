from typing import Protocol, runtime_checkable
from src.auth.infrastructure.persistence.postgres.models import UserTokens

@runtime_checkable
class TokenProtocol(Protocol):
    """
    Contrato para servicios de autenticación mediante tokens.
    
    ¿Qué es?
    --------
    Define la interfaz que CUALQUIER servicio de tokens debe cumplir.
    Puede ser JWT, OAuth2, SessionTokens, API Keys, etc.
    
    ¿Cómo implementar?
    ------------------
    1. Crea una clase que implemente estos cuatro métodos
    2. Asegúrate de cumplir exactamente las firmas
    3. Registra la clase en dependencies.py
    
    Nota: Los métodos privados (como _encode_token) NO son parte del Protocol.
          Cada implementación puede tener sus propios helpers internos.
    
    Ejemplo de implementación (JWT):
    
    class TokenService:
        def __init__(self, settings: Settings):
            self.settings = settings
        
        def create_access_token(self, user_id: str) -> str:
            # Crea JWT con duración corta
            return self._encode_token({...}, timedelta(minutes=15))
        
        def create_refresh_token(self, user_id: str) -> str:
            # Crea JWT con duración larga
            return self._encode_token({...}, timedelta(days=7))
        
        def get_user_id_from_access_token(self, token: str) -> str:
            # Decodifica JWT y extrae user_id
            payload = self.decode_token(token)
            return payload.get("sub")
        
        def get_user_id_from_refresh_token(self, token: str) -> str:
            # Decodifica JWT y extrae user_id
            payload = self.decode_token(token)
            return payload.get("sub")
    
    Atributos requeridos:
    --------------------
    Ninguno. Solo implementa los métodos.
    
    Métodos requeridos:
    -------------------
    """
    def create_user_tokens(self, user_id:int) -> UserTokens:
        ...
    
    def create_access_token(self, user_id: str) -> str:
        """
        Genera un token de acceso de corta duración para autenticar solicitudes.
        
        Parámetros:
        -----------
        user_id : str
            ID único del usuario en tu sistema.
            Típicamente: str(usuario.id_usuario)
            
            Nota: Se serializa en el token para que pueda recuperarse después.
        
        Retorna:
        --------
        str
            Token de acceso en formato cadena.
            
            Ejemplos por algoritmo:
            
            JWT:     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidHlwZSI6ImFjY2VzcyJ9...."
            OAuth2:  "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            Session: "sess_abc123xyz789"
        
        Características del token:
        --------------------------
        - Contiene el user_id codificado (recuperable con get_user_id_from_access_token)
        - Duración CORTA (típicamente 15-30 minutos)
        - Se envía en requests posteriores en header Authorization
        - Expiración automática (no requiere logout)
        - No modificable por el cliente (firmado/encriptado)
        
        Excepciones esperadas:
        ----------------------
        Exception (genérica)
            Si hay error durante la generación (credenciales inválidas, etc.)
        
        Ejemplo práctico:
        -----------------
        # En AuthService.register()
        token = self.token_service.create_access_token(
            user_id=str(usuario_creado.id_usuario)
        )
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
        # Se usa para enviar email de verificación
        url_verificacion = f"{settings.BASE_URL}/verificar/{token}"
        
        Ciclo de vida:
        ---------------
        1. Usuario se registra → create_access_token()
        2. Token se envía en email/respuesta
        3. Usuario usa token en requests (Authorization: Bearer <token>)
        4. Servidor valida token con get_user_id_from_access_token()
        5. Token expira (no se puede usar después)
        6. Usuario usa refresh_token para obtener nuevo access_token
        
        Notas de implementación:
        -----------------------
        - El access token es de corta duración (no puede ser indefinido)
        - Debe contener user_id de forma codificada/encriptada
        - El cliente recibe el token y lo almacena (típicamente en memoria)
        - El cliente envía el token en cada request autenticado
        - El servidor NUNCA almacena el token (stateless)
        """
        ...
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Genera un token de larga duración para obtener nuevos access tokens.
        
        Parámetros:
        -----------
        user_id : str
            ID único del usuario.
            Típicamente: str(usuario.id_usuario)
        
        Retorna:
        --------
        str
            Token de refresco en formato cadena.
            Similar a access_token pero con duración más larga.
        
        Características del token:
        --------------------------
        - Contiene el user_id codificado
        - Duración LARGA (típicamente 7-30 días)
        - Se almacena en cookie HttpOnly (seguro contra XSS)
        - No se usa directamente, solo para obtener nuevos access_tokens
        - Expiración automática
        
        Ejemplo práctico:
        -----------------
        # En AuthService.login() o register()
        tokens = UserTokens(
            access_token=self.token_service.create_access_token(str(usuario.id_usuario)),
            refresh_token=self.token_service.create_refresh_token(str(usuario.id_usuario))
        )
        
        # tokens.access_token: Corta duración, para requests
        # tokens.refresh_token: Larga duración, almacenada en cookie
        
        Ciclo de vida:
        ---------------
        1. Usuario login → Se generan access_token + refresh_token
        2. Ambos se retornan al cliente
        3. Cliente usa access_token para requests autenticados
        4. Cuando access_token expira (15min), cliente usa refresh_token
        5. Servidor valida refresh_token
        6. Si es válido, genera nuevo access_token (sin logout)
        7. Si es inválido, usuario debe hacer login nuevamente
        
        Notas de implementación:
        -----------------------
        - Duración MUCHO más larga que access_token
        - Típicamente se almacena en cookie HttpOnly
        - El cliente NO lo debe usar directamente (no en Authorization header)
        - Solo se usa en endpoint /refresh para obtener nuevo access_token
        - Protege contra expiración frecuente de access_tokens
        """
        ...
    
    def get_user_id_from_access_token(self, token: str) -> str:
        """
        Extrae el user_id de un token de acceso válido.
        
        Parámetros:
        -----------
        token : str
            Token de acceso generado por create_access_token().
            Ejemplo: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            
            Nota: Debe ser un token válido y no expirado.
        
        Retorna:
        --------
        str
            ID del usuario extraído del token.
            Ejemplo: "123"
            
            Nota: Retorna string, aunque el ID sea numerico.
                  El cliente debe convertir si es necesario: int(user_id)
        
        Excepciones esperadas:
        ----------------------
        TokenInvalido
            Si el token no es válido (formato incorrecto)
        
        TokenExpirado
            Si el token ha expirado
        
        Exception (genérica)
            Si hay error al decodificar/validar
        
        Ejemplo práctico:
        -----------------
        # En un endpoint que requiere autenticación
        @router.get("/usuarios/me")
        async def get_me(
            token: str = Depends(get_token_from_header),
            auth_service: AuthService = Depends(get_auth_service)
        ):
            try:
                user_id = auth_service.token_service.get_user_id_from_access_token(token)
                # user_id = "123"
                
                usuario = auth_service.get_user(AuthUser(id_usuario=int(user_id)))
                return usuario
            
            except TokenInvalido:
                raise HTTPException(status_code=401, detail="Token inválido")
            except TokenExpirado:
                raise HTTPException(status_code=401, detail="Token expirado")
        
        Flujo en verificación de email:
        --------------------------------
        # En AuthService.verificar_mail()
        user_id_db = self.token_service.get_user_id_from_access_token(token)
        # user_id_db = "123"
        
        usuario = self.user_repository.obtener_por_id_sin_activar(int(user_id_db))
        usuario = self.user_repository.activar(usuario)
        
        Notas de implementación:
        -----------------------
        - Debe decodificar/validar el token
        - Extraer el claim "sub" (subject = user_id)
        - Validar que el token no ha expirado
        - Validar que es de tipo "access" (no refresh)
        - Si algo falla, lanza TokenInvalido o TokenExpirado
        - El método es stateless (no consulta BD)
        """
        ...
    
    def get_user_id_from_refresh_token(self, token: str) -> str:
        """
        Extrae el user_id de un token de refresco válido.
        
        Parámetros:
        -----------
        token : str
            Token de refresco generado por create_refresh_token().
            Típicamente viene de una cookie HttpOnly.
            Ejemplo: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
        Retorna:
        --------
        str
            ID del usuario extraído del token.
            Ejemplo: "123"
        
        Excepciones esperadas:
        ----------------------
        TokenInvalido
            Si el token no es válido
        
        TokenExpirado
            Si el token ha expirado (usuario debe hacer login nuevamente)
        
        Exception (genérica)
            Si hay error al decodificar
        
        Ejemplo práctico:
        -----------------
        # En endpoint POST /refresh
        @router.post("/refresh")
        async def refresh_access_token(
            refresh_token: str = Cookie(...),
            auth_service: AuthService = Depends(get_auth_service)
        ):
            try:
                user_id = auth_service.token_service.get_user_id_from_refresh_token(refresh_token)
                # user_id = "123"
                
                # Generar nuevo access_token
                new_access_token = auth_service.token_service.create_access_token(user_id)
                
                return {"access_token": new_access_token}
            
            except TokenExpirado:
                # El refresh_token expiró, usuario debe hacer login
                raise HTTPException(status_code=401, detail="Sesión expirada")
            except TokenInvalido:
                raise HTTPException(status_code=401, detail="Token inválido")
        
        Flujo en AuthService.refreshed_token():
        ----------------------------------------
        # En AuthService.refreshed_token()
        user_id = self.token_service.get_user_id_from_refresh_token(refresh_token)
        # user_id = "123"
        
        new_access_token = self.token_service.create_access_token(user_id)
        self.cookies.set_access_cookie(response, new_access_token)
        # Nuevo access_token guardado en cookie
        
        Diferencia vs get_user_id_from_access_token:
        -----------------------------------------------
        | Aspecto | Access Token | Refresh Token |
        |---------|--------------|---------------|
        | Duración | Corta (15min) | Larga (7 días) |
        | Uso | Requests autenticados | Solo para refrescar |
        | Ubicación | Authorization header | Cookie HttpOnly |
        | Expiración | Frecuente | Rara |
        
        Notas de implementación:
        -----------------------
        - Muy similar a get_user_id_from_access_token
        - Posiblemente valida que tipo = "refresh" (en algunos sistemas)
        - Duración más larga (no expira tan rápido)
        - Si expira, usuario debe hacer login nuevamente
        - El método es stateless (no consulta BD)
        """
        ...