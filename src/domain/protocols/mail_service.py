from typing import Protocol, runtime_checkable

@runtime_checkable
class MailProtocol(Protocol):
    """
    Contrato para servicios de envío de correos electrónicos.
    
    ¿Qué es?
    --------
    Define la interfaz que CUALQUIER servicio de correos debe cumplir.
    Puede ser FastAPI-Mail, SendGrid, AWS SES, Mailgun, SMTP local, etc.
    
    ¿Cómo implementar?
    ------------------
    1. Crea una clase que implemente estos dos métodos
    2. Asegúrate de cumplir exactamente las firmas
    3. Registra la clase en dependencies.py
    
    Ejemplo de implementación (FastAPI-Mail):
    
    class MailService:
        def __init__(self, settings: Settings):
            self.settings = settings
            # Configura credenciales del proveedor
            self.cfg = ConnectionConfig(...)
            self.fast_mail = FastMail(self.cfg)
        
        async def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto: str) -> None:
            # 1. Forma el mensaje con los parámetros
            # 2. Envía usando FastMail
            pass
        
        def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
            # 1. Carga template HTML (Jinja2, etc.)
            # 2. Renderiza con URL y nombre del proyecto
            # 3. Retorna HTML como string
            pass
    
    Atributos requeridos:
    --------------------
    Ninguno. Solo implementa los métodos.
    
    Métodos requeridos:
    -------------------
    """
    
    async def enviar_mail(self, email_destino: str, cuerpo_html: str, asunto: str) -> None:
        """
        Envía un correo electrónico a un destinatario.
        
        Parámetros:
        -----------
        email_destino : str
            Email del destinatario.
            Formato esperado: "usuario@ejemplo.com"
            Validación: Puede haber validación básica o no,
                       depende del proveedor.
        
        cuerpo_html : str
            Contenido del correo en formato HTML.
            Puede incluir estilos CSS inline, imágenes, links, etc.
            Generalmente obtenido de generar_correo_verificacion() u otro generador.
            
            Ejemplo:
            "<html><body><h1>Bienvenido!</h1><a href='...'>Verificar</a></body></html>"
        
        asunto : str
            Línea de asunto del correo.
            Este texto es lo que ve el usuario en su bandeja de entrada.
            
            Nota: Algunos proveedores pueden agregar automáticamente
                  el nombre de la aplicación al asunto.
            
            Ejemplo: "Activa tu cuenta"
                     Puede convertirse en: "Activa tu cuenta - MyApp"
        
        Retorna:
        --------
        None
            Este método es fire-and-forget.
            No retorna información sobre el envío.
            Si falla, lanza una excepción.
        
        Excepciones esperadas:
        ----------------------
        Exception (genérica o específica del proveedor)
            Si hay error en:
            - Credenciales inválidas (usuario/contraseña SMTP)
            - Email destinatario inválido
            - Conexión al servidor de correos fallida
            - Límite de envíos superado
            - HTML malformado o muy grande
        
        Comportamiento asincrónico:
        ---------------------------
        Este método es async porque enviar correos es una operación I/O
        que puede tomar tiempo. No bloquea la ejecución del programa.
        
        Ejemplo de uso:
        ---------------
        >>> mail_service = MailService(settings)
        >>> html = mail_service.generar_correo_verificacion(
        ...     url="https://miapp.com/verificar/token123",
        ...     nombre_proyecto="MiApp"
        ... )
        >>> await mail_service.enviar_mail(
        ...     email_destino="juan@example.com",
        ...     cuerpo_html=html,
        ...     asunto="Activa tu cuenta"
        ... )
        # Correo enviado exitosamente
        
        Notas de implementación:
        -----------------------
        - Asegúrate de que el proveedor esté configurado con credenciales válidas
        - El cuerpo_html debe ser HTML válido (aunque algunos proveedores son tolerantes)
        - El asunto debe ser descriptivo y conciso
        - Algunos proveedores permiten templates, otros solo HTML plano
        - Considera timeouts si el servidor de correos es lento
        - Log errores para debugging
        """
        ...
    
    def generar_correo_verificacion(self, url: str, nombre_proyecto: str) -> str:
        """
        Genera el contenido HTML de un correo de verificación de email.
        
        Parámetros:
        -----------
        url : str
            URL completa que el usuario debe visitar para verificar su email.
            Esta URL típicamente contiene un token de verificación.
            
            Formato esperado: "https://miapp.com/usuarios/verificar/abc123xyz"
            
            Notas:
            - Debe ser una URL válida y accesible
            - Debe incluir el protocolo (http:// o https://)
            - El cliente (AuthService) construye esta URL antes de pasarla
        
        nombre_proyecto : str
            Nombre de tu aplicación/proyecto.
            Se usa para personalizar el contenido del correo.
            
            Ejemplo: "MiApp", "TuSistema", "MyPlatform"
            Se mostrará al usuario como parte del mensaje.
        
        Retorna:
        --------
        str
            HTML completo del correo como string.
            Este HTML será enviado como cuerpo_html a enviar_mail().
            
            Características esperadas del HTML:
            - Debe contener el URL pasado (como link clickeable)
            - Debe contener el nombre_proyecto
            - Debe ser responsive (verse bien en mobile)
            - Puede incluir estilos CSS inline
            - Puede incluir logo, imágenes, etc.
        
        Excepciones esperadas:
        ----------------------
        FileNotFoundError
            Si el template HTML no existe (si usas archivos de template)
        
        TemplateError (o equivalente)
            Si hay error al renderizar el template (variables faltantes, etc.)
        
        Exception
            Si hay error al cargar configuración o recursos
        
        Ejemplo de uso:
        ---------------
        >>> mail_service = MailService(settings)
        >>> html = mail_service.generar_correo_verificacion(
        ...     url="https://myapp.com/verify/token123abc",
        ...     nombre_proyecto="MyApp"
        ... )
        >>> print(type(html))
        <class 'str'>
        >>> print(html[:100])  # Primeros 100 caracteres
        '<html><head><style>...</style></head><body><h1>Bienvenido a MyApp</h1>...'
        
        >>> # Luego este HTML se pasa a enviar_mail()
        >>> await mail_service.enviar_mail(
        ...     email_destino="usuario@example.com",
        ...     cuerpo_html=html,
        ...     asunto="Verifica tu email"
        ... )
        
        Notas de implementación:
        -----------------------
        - Típicamente carga un template HTML (Jinja2, Mako, etc.)
        - Renderiza el template con las variables url y nombre_proyecto
        - Retorna el HTML renderizado como string puro
        - No envía nada, solo genera el contenido
        
        Ejemplo de flujo completo en AuthService:
        -----------------------------------------
        # En AuthService.register()
        token = self.token_service.create_access_token(usuario.id)
        
        # 1. Construye la URL
        url_verificacion = f"{settings.BASE_URL}/usuarios/verificar/{token}"
        
        # 2. Genera el HTML
        cuerpo_html = self.mail_service.generar_correo_verificacion(
            url=url_verificacion,
            nombre_proyecto=settings.NOMBRE_APP
        )
        
        # 3. Envía el correo
        await self.mail_service.enviar_mail(
            email_destino=usuario.email,
            cuerpo_html=cuerpo_html,
            asunto="Activa tu cuenta"
        )
        """
        ...
