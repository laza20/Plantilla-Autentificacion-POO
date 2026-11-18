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
    
 
 