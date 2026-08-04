# Auth Con POO SOLID — Plantilla de Autenticación FastAPI (Clean Architecture + SOLID)

## 1. Introducción y Objetivo General

Este repositorio es una **plantilla (boilerplate) de autenticación y autorización** construida con **FastAPI** y **PostgreSQL**, diseñada explícitamente para ser **reutilizada entre múltiples proyectos/clientes**, en lugar de ser una solución de un solo uso.

El objetivo técnico central del proyecto es demostrar cómo se puede construir un módulo de autenticación completo (registro, verificación por correo, login, refresh de tokens y logout) **sin acoplar la lógica de negocio al framework ni a proveedores externos concretos**. Esto se logra aplicando **Clean Architecture**, los principios **SOLID** y, en particular, el **Principio de Inversión de Dependencias (DIP)** implementado mediante `typing.Protocol` de Python — es decir, contratos estructurales (*duck typing* tipado) en lugar de herencia de clases abstractas (`ABC`).

En términos prácticos, esto significa que:

- Los **Casos de Uso** (`RegisterUseCase`, `LoginUseCase`, etc.) no saben si las contraseñas se hashean con Argon2 o Bcrypt, si los correos se envían con FastAPI-Mail o SendGrid, o si las imágenes se guardan en Cloudinary o S3. Solo conocen **protocolos**.
- Cambiar de proveedor (por ejemplo, migrar de Cloudinary a AWS S3) implica crear una nueva clase que cumpla el `ImageProtocol` y modificar **una sola línea** en el contenedor de dependencias — sin tocar la capa de aplicación ni la de dominio.
- El dominio (reglas de negocio puras, como la política de contraseñas) es, con una excepción menor señalada en la Sección 14, independiente de FastAPI.

Esta plantilla resuelve el problema recurrente de tener que reescribir el mismo flujo de autenticación (registro + verificación de email + JWT con access/refresh token + cookies HttpOnly) en cada nuevo proyecto backend, ofreciendo en su lugar un punto de partida arquitectónicamente sólido, testeable y extensible.

---

## 2. Características Principales y Stack Tecnológico

### Características principales

- Registro de usuarios con **carga de imagen de perfil opcional** vía `multipart/form-data`.
- **Verificación de cuenta por correo electrónico** con plantilla HTML (Jinja2) y token firmado.
- **Login** basado en `OAuth2PasswordRequestForm` (estándar de FastAPI/OpenAPI).
- **JWT de doble token**: Access Token (corta duración) + Refresh Token (larga duración), gestionados como **cookies `HttpOnly`**, no expuestos al cliente JavaScript.
- **Renovación silenciosa de sesión** (`/Refresh/Token`) sin requerir nuevo login.
- **Logout** que invalida la sesión eliminando las cookies.
- **Hashing de contraseñas con Argon2** (vía `pwdlib`), el algoritmo recomendado actualmente por OWASP.
- **Política de contraseñas** configurable en el dominio (longitud, mayúsculas, minúsculas, dígitos, símbolos).
- **Subida de imágenes a Cloudinary** con validación de tamaño y extensión antes del envío.
- **Manejo de errores centralizado**: toda excepción de dominio (`DomainError`) se traduce automáticamente a una respuesta HTTP coherente mediante un `exception_handler` global.
- **Guards de autorización** (`get_current_user`, `get_admin_user`, `get_premium_user`) listos para proteger endpoints.
- **Inyección de dependencias 100% vía FastAPI `Depends`**, sin frameworks de DI adicionales.

### Stack tecnológico (extraído de `requirements.txt`)

| Categoría | Tecnología | Rol en el proyecto |
|---|---|---|
| Framework web | `fastapi==0.136.1` | Enrutamiento HTTP, validación, inyección de dependencias |
| Servidor ASGI | `uvicorn==0.46.0` | Servidor de desarrollo/producción |
| ORM / Modelado | `sqlmodel==0.0.38` | Combina Pydantic + SQLAlchemy para modelos tipados |
| SQL Toolkit | `SQLAlchemy==2.0.49` | Motor subyacente de `sqlmodel` |
| Driver PostgreSQL | `psycopg2-binary==2.9.12` | Conexión al motor PostgreSQL |
| Migraciones | `alembic==1.18.4` | Declarado como dependencia (ver nota en Sección 10) |
| JWT | `python-jose==3.5.0` | Codificación/decodificación de tokens JWT |
| Hashing de contraseñas | `pwdlib==0.3.0` + `argon2-cffi==25.1.0` | Hash y verificación Argon2 |
| Envío de correo | `fastapi-mail==1.6.4` + `aiosmtplib==5.1.1` | Envío asíncrono de correos SMTP |
| Plantillas de correo | `Jinja2==3.1.6` | Renderizado del HTML de verificación |
| Imágenes en la nube | `cloudinary==1.44.2` | Almacenamiento y transformación de imágenes |
| Configuración | `pydantic-settings==2.14.1` | Lectura y validación tipada de variables de entorno |
| Validación de datos | `pydantic==2.13.4` | Modelos de entrada/salida (DTOs) |
| Multipart / formularios | `python-multipart==0.0.28` | Soporte para `Form()` y `UploadFile` |
| Manejo de imágenes | `pillow==12.2.0` | Dependencia transitiva para procesamiento de imágenes |
| Utilidades | `python-dotenv==1.2.2` | Carga de archivo `.env` |

**Lenguaje:** Python (tipado con `typing.Protocol`, `Optional`, uniones `str | None`, propio de Python 3.10+).

---

## 3. Arquitectura del Sistema

### 3.1 Patrón arquitectónico identificado

El proyecto implementa una variante de **Clean Architecture** (también reconocible como **Arquitectura por Capas con Inversión de Dependencias**, cercana a **Hexagonal/Ports & Adapters**). La evidencia concreta en el código:

1. **Existe una capa de Dominio pura** (`src/auth/domain/`) que define **Protocolos** (`Protocol` de `typing`) como "puertos": `UserRepositoryProtocol`, `TokenProtocol`, `PasswordProtocol`, `MailProtocol`, `ImageProtocol`. Estos protocolos son los **contratos** que la capa de aplicación consume, y que la infraestructura debe satisfacer.
2. **Existe una capa de Aplicación** (`src/auth/application/`) formada por **Casos de Uso** (`RegisterUseCase`, `LoginUseCase`, `LogoutUseCase`, `RefreshTokenUseCase`, `VerifyMailUseCase`), cada uno con una única responsabilidad de orquestación, recibiendo sus dependencias exclusivamente como **protocolos** (nunca clases concretas) por constructor.
3. **Existe una capa de Infraestructura** (`src/auth/infrastructure/`) que contiene las implementaciones concretas: `UserRepository` (PostgreSQL/SQLModel), `TokenService` (JWT), `PasswordService` (Argon2), `MailService` (FastAPI-Mail), `ImageService` (Cloudinary). Ninguna de estas clases se referencia por su tipo concreto en la capa de Aplicación — solo se inyectan cumpliendo el protocolo correspondiente.
4. **Existe una capa de Presentación** (`src/auth/presentation/web/`) que es la única capa que "conoce" FastAPI explícitamente: `routers.py` (endpoints HTTP), `guards.py` (dependencias de autorización), `cookies/cookies.py` (gestión de cookies de sesión).
5. **Existe un mecanismo explícito de Composición/Ensamblado** (`src/container/`), que actúa como el punto donde todas las capas se "cablean" entre sí (Dependency Injection Composition Root).

### 3.2 Responsabilidad detallada de cada capa

| Capa | Carpeta | Responsabilidad | ¿Conoce FastAPI? | ¿Conoce infraestructura concreta? |
|---|---|---|---|---|
| **Dominio** | `auth/domain/` | Reglas de negocio, contratos (Protocols), excepciones de dominio | No (excepción menor, ver 3.3) | No — solo define interfaces |
| **Aplicación** | `auth/application/` | Orquesta un caso de uso completo llamando a protocolos | Parcialmente (usa `Response`, `UploadFile` como tipos de FastAPI/Starlette en firmas) | No — solo recibe protocolos por constructor |
| **Infraestructura** | `auth/infrastructure/` | Implementaciones concretas: JWT, Argon2, Cloudinary, FastAPI-Mail, SQLModel | Sí (algunos `Depends` locales) | Sí — es la capa que integra proveedores reales |
| **Presentación** | `auth/presentation/web/` | Define endpoints, extrae parámetros HTTP, delega a Casos de Uso | Sí, totalmente | No directamente — recibe Casos de Uso ya construidos |
| **Composición** | `container/` | Ensambla instancias concretas para satisfacer los protocolos que exige cada Caso de Uso | Sí (usa `Depends`) | Sí — es el único lugar donde dominio e infraestructura se "encuentran" |

### 3.3 Reglas de dependencia y flujo de comunicación

La regla de dependencia de Clean Architecture se cumple **de afuera hacia adentro**:

```
Presentación  →  Aplicación  →  Dominio
Infraestructura  →  Dominio  (implementa los Protocols)
Composición (container)  →  conoce TODAS las capas (es el único punto permitido)
```

- La capa de **Dominio** no importa nada de `infrastructure/` ni de `presentation/`. Solo depende de `fastapi.UploadFile` en `image_service.py` (protocolo `ImageProtocol`) y de `fastapi.HTTPException`/`status` en `domain/exceptions/domain.py`. Esta es la única fuga de framework detectada dentro del dominio: es menor (tipos de datos, no lógica de FastAPI) pero rompe la pureza teórica total de la capa de dominio. Se documenta como observación en la Sección 14.
- La capa de **Aplicación** (Casos de Uso) depende exclusivamente de **Protocolos** del dominio (`UserRepositoryProtocol`, `TokenProtocol`, etc.), de modelos de datos (`AuthUser`, `UserRegisterDTO`, etc.) y de servicios de dominio (`PasswordPolicyService`, `UserValidationService`). Nunca importa una clase concreta de `infrastructure/`.
- La capa de **Infraestructura** importa los Protocols del dominio para garantizar que sus clases cumplen el contrato esperado (aunque, al ser `Protocol` estructural, **no requiere herencia explícita** — el cumplimiento es implícito por firma de métodos).
- El **Contenedor de Dependencias** (`container/`) es el único módulo que importa simultáneamente Protocolos, implementaciones concretas y Casos de Uso, actuando como *Composition Root*.

Esto habilita la **Inversión de Dependencias (DIP)**: el Caso de Uso de alto nivel (`LoginUseCase`) no depende de un módulo de bajo nivel (`TokenService` con JWT), sino de una abstracción (`TokenProtocol`) — y es la infraestructura la que depende de esa abstracción para saber qué debe implementar.

---

## 4. Estructura de Carpetas y Directorios

```
.
├── .gitignore
├── README.md
├── requirements.txt
│
└── src/
    ├── main.py                              # Punto de entrada: crea la app FastAPI y registra el router + exception handler global
    │
    ├── config/
    │   └── config.py                        # Settings (pydantic-settings) — lee y valida el .env
    │
    ├── container/                           # Composition Root — cablea Protocolos con implementaciones concretas
    │   ├── auth_container.py                # Clases "Container*" que ensamblan cada Caso de Uso
    │   └── providers.py                      # Funciones factory usadas como Depends() en los routers
    │
    ├── database/
    │   ├── client.py                        # engine de SQLModel + get_session() (generador de sesión)
    │   └── enums/
    │       └── estado_entidad.py            # Enum EstadoEntidad (activo, eliminado, reportado, suspendido, pendiente)
    │
    └── auth/
        ├── domain/                          # ── CAPA DE DOMINIO (núcleo, sin infraestructura) ──
        │   ├── protocols/                   # "Puertos" — contratos que la infraestructura debe cumplir
        │   │   ├── auth_user_repository.py       # UserRepositoryProtocol
        │   │   ├── token_service.py         # TokenProtocol
        │   │   ├── password_service.py      # PasswordProtocol
        │   │   ├── mail_service.py          # MailProtocol
        │   │   └── image_service.py         # ImageProtocol
        │   ├── services/                    # Servicios de dominio (reglas de negocio puras)
        │   │   ├── password_policy.py       # PasswordPolicyService
        │   │   └── user_validation_service.py  # UserValidationService
        │   └── exceptions/                  # Jerarquía de excepciones de negocio
        │       ├── domain.py                # DomainError (base) y subclases genéricas
        │       ├── tokens.py                # TokenException y subclases relacionadas a tokens
        │       └── usuarios_exceptions.py   # UsuarioError y subclases relacionadas a usuarios/auth
        │
        ├── application/                     # ── CAPA DE APLICACIÓN (orquestación) ──
        │   ├── dtos.py                      # parse_usuario_form — adapta multipart/form-data a UserRegisterDTO
        │   └── use_cases/
        │       ├── register.py              # RegisterUseCase
        │       ├── login.py                 # LoginUseCase
        │       ├── logout.py                # LogoutUseCase
        │       ├── refresh_token.py         # RefreshTokenUseCase
        │       └── verify_email.py          # VerifyMailUseCase
        │
        ├── infrastructure/                  # ── CAPA DE INFRAESTRUCTURA (implementaciones concretas) ──
        │   ├── persistence/postgres/
        │   │   ├── models.py                # AuthUser (tabla) + DTOs de entrada/salida (SQLModel)
        │   │   └── auth_user_repository.py       # UserRepository — implementa UserRepositoryProtocol
        │   ├── security/
        │   │   ├── security.py              # PasswordService (Argon2) — implementa PasswordProtocol
        │   │   └── tokens/
        │   │       └── tokens.py            # TokenService (JWT) — implementa TokenProtocol
        │   ├── mail/
        │   │   └── mail.py                  # MailService (FastAPI-Mail + Jinja2) — implementa MailProtocol
        │   ├── images/
        │   │   ├── cloudinary_config.py     # Configuración global del SDK de Cloudinary
        │   │   └── cloudinary.py            # ImageService — implementa ImageProtocol
        │   └── templates/
        │       └── verificacion.html        # Plantilla Jinja2 del correo de verificación
        │
        └── presentation/web/                # ── CAPA DE PRESENTACIÓN (HTTP/FastAPI) ──
            ├── routers.py                   # Endpoints públicos del módulo de usuarios
            ├── guards.py                    # AuthDependencies — dependencias de autorización
            └── cookies/
                └── cookies.py               # CookiesService — set/delete de cookies de sesión
```

### Semántica de las carpetas clave

- **`domain/protocols/`**: es el corazón del DIP. Cada archivo contiene una interfaz (`Protocol`) **extensamente documentada con docstrings** que funcionan como especificación para cualquier desarrollador que desee crear una nueva implementación (por ejemplo, un `S3ImageService` que cumpla `ImageProtocol`).
- **`domain/exceptions/`**: centraliza todos los errores de negocio en una jerarquía común (`DomainError`), lo que permite un manejo de errores **uniforme y declarativo** (ver Sección 6.4).
- **`application/use_cases/`**: cada archivo = un flujo de negocio completo, con un único método público (`register`, `login`, `logout`, `refreshed_token`, `verificar_mail`).
- **`container/`**: separa "qué instancias construir" (`providers.py`, funciones `Depends`-compatibles) de "cómo se ensamblan en un Caso de Uso" (`auth_container.py`, clases `Container*`).
- **`infrastructure/`**: aquí — y solo aquí — aparecen los SDKs de terceros (`cloudinary`, `jose`, `pwdlib`, `fastapi_mail`).

---

## 5. Ciclo de Vida de una Petición (Flujo de Ejecución)

### 5.1 Explicación paso a paso (caso: Login)

1. El cliente envía `POST /{NOMBRE_APP}/usuarios/login` con `username` (email) y `password` en formato `application/x-www-form-urlencoded` (estándar `OAuth2PasswordRequestForm`).
2. FastAPI enruta la petición a `routers.py :: logearse()`.
3. FastAPI resuelve la dependencia `Depends(get_login_use_case)` **antes** de ejecutar la función del endpoint. Esto dispara una cadena de resolución definida en `providers.py`:
   - `get_settings()` → instancia única de `Settings`.
   - `get_auth_user_repository()` → construye `UserRepository(session)`, donde `session` proviene de `get_session()` (generador con `yield`, ciclo de vida por petición).
   - `get_token_service()` → construye `TokenService(settings)`, devuelto **tipado como `TokenProtocol`**.
   - `get_password_service()` → construye `PasswordService(settings)`, tipado como `PasswordProtocol`.
   - `get_cookies_service()` → construye `CookiesService(settings)`.
   - `get_user_validation_service()` → construye `UserValidationService(repository, settings)`.
4. Con todas esas piezas resueltas, `get_login_use_case()` las pasa a `ContainerLogin(...)`, cuya propiedad `.login_use_case` construye y retorna la instancia final de `LoginUseCase`.
5. FastAPI inyecta ese `LoginUseCase` ya completamente ensamblado en el parámetro `login_use_case` del endpoint.
6. El endpoint llama a `login_use_case.login(usuario.username, usuario.password, response)`.
7. Dentro del Caso de Uso (capa de Aplicación, **sin conocimiento de HTTP salvo el objeto `Response` para setear cookies**):
   a. `UserValidationService.obtener_usuario_existente(mail)` busca al usuario vía `UserRepositoryProtocol.obtener_por_email()` y lanza `UsuarioNoEncontrado` si no existe.
   b. `PasswordProtocol.verify_password(password, hash_almacenado)` valida la contraseña (implementado con Argon2).
   c. Si la contraseña es incorrecta, se lanza `LoginError`.
   d. `TokenProtocol.create_user_tokens(user_id)` genera el par access/refresh token (JWT).
   e. `CookiesService.set_auth_cookies(response, access, refresh)` adjunta ambos tokens como cookies `HttpOnly` a la respuesta.
8. El Caso de Uso retorna un `LoginResponse` (tokens + datos públicos del usuario).
9. Si en cualquier punto se lanzó una excepción que hereda de `DomainError`, la ejecución nunca llega al `try/except` local del endpoint (los routers no capturan estas excepciones): es interceptada por el **exception handler global** registrado en `main.py`, que traduce automáticamente `exc.status_code` y `exc.message` a una respuesta JSON estándar.

### 5.2 Diagrama textual del recorrido de datos

```
Cliente HTTP
    │
    │  POST /{NOMBRE_APP}/usuarios/login
    ▼
┌──────────────────────────────────────────────┐
│ presentation/web/routers.py :: logearse()    │   ← Capa de Presentación
│   Depends(get_login_use_case)                │
└──────────────────────────────────────────────┘
    │  FastAPI resuelve el árbol de Depends
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ container/providers.py :: get_login_use_case                                │
│   ├─ get_settings()                                                         │
│   ├─ get_auth_user_repository()   → UserRepository                               │
│   ├─ get_token_service()     → TokenService (protocolo TokenProtocol)       │
│   ├─ get_password_service()  → PasswordService (protocolo PasswordProtocol) │
│   ├─ get_cookies_service()   → CookiesService                               │
│   └─ get_user_validation_service()                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    │  construye
    ▼
┌───────────────────────────────────────────────┐
│ container/auth_container.py :: ContainerLogin │
│   .login_use_case  →  LoginUseCase(...)       │
└───────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ application/use_cases/login.py :: LoginUseCase   │   ← Capa de Aplicación
│   1. UserValidationService.obtener_usuario_...   │   (Servicio de Dominio)
│   2. PasswordProtocol.verify_password(...)       │   (contrato)
│   3. TokenProtocol.create_user_tokens(...)       │   (contrato)
│   4. CookiesService.set_auth_cookies(...)        │
└──────────────────────────────────────────────────┘
    │                                            │
    │ implementado por                           │ implementado por
    ▼                                            ▼
┌─────────────────────────────────────────┐   ┌─────────────────────────────────────────┐
│ infrastructure/security/                │   │ infrastructure/security/                │ ← Capa de 
│ security.py :: PasswordService (Argon2) │   │ tokens/tokens.py :: TokenService (JWT)  │  Infraestructura
└─────────────────────────────────────────┘   └─────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────┐
│ infrastructure/persistence/        │
│ postgres/auth_user_repository.py        │   ← Infraestructura de Persistencia
│ UserRepository.obtener_por_email() │
└────────────────────────────────────┘
    │
    ▼
┌───────────────────────┐
│        PostgreSQL     │
└───────────────────────┘
    │
    ▼
Respuesta JSON (LoginResponse) + Set-Cookie: access_token / refresh_token (HttpOnly)
```

Si en el paso 7 se lanza cualquier `DomainError` (por ejemplo `LoginError` o `UsuarioNoEncontrado`), el flujo se desvía instantáneamente:

```
DomainError lanzada en cualquier capa
    ▼
main.py :: domain_error_handler(request, exc)
    ▼
JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
```

---

## 6. Análisis Detallado de Módulos y Capas

### 6.1 Dominio — Protocolos (`domain/protocols/`)

Los cinco protocolos usan el decorador `@runtime_checkable` sobre `typing.Protocol`, lo que permite verificar en tiempo de ejecución (con `isinstance`) si un objeto cumple la interfaz, aunque en la práctica el proyecto confía en el **tipado estático** (Python duck-typing) sin ejecutar dichas comprobaciones activamente.

| Protocolo | Métodos exigidos | Implementación concreta actual |
|---|---|---|
| `UserRepositoryProtocol` | `insertar`, `obtener_por_id_sin_activar`, `activar`, `obtener_por_email`, `obtener_por_id` | `UserRepository` (SQLModel/PostgreSQL) |
| `TokenProtocol` | `create_user_tokens`, `create_access_token`, `create_refresh_token`, `get_user_id_from_access_token`, `get_user_id_from_refresh_token` | `TokenService` (JWT vía `python-jose`) |
| `PasswordProtocol` | `hash_password`, `verify_password` | `PasswordService` (Argon2 vía `pwdlib`) |
| `MailProtocol` | `enviar_mail` (async), `generar_correo_verificacion` | `MailService` (FastAPI-Mail + Jinja2) |
| `ImageProtocol` | `insertar_imagen` | `ImageService` (Cloudinary) |

Cada protocolo incluye **docstrings extensísimos** (parámetros, tipos de retorno, excepciones esperadas, ejemplos de uso) que funcionan como una guía de implementación autocontenida — un patrón poco común pero muy valioso para una plantilla reutilizable, ya que cualquier desarrollador puede crear un proveedor alternativo leyendo únicamente el contrato, sin inspeccionar la implementación de referencia.

> **Nota de diseño en `TokenProtocol`**: declara `create_user_tokens` sin docstring (a diferencia del resto de métodos, extensamente documentados), una inconsistencia menor de documentación.

### 6.2 Dominio — Servicios (`domain/services/`)

- **`PasswordPolicyService.validar(contraseña)`**: valida, mediante expresiones regulares, que la contraseña tenga ≥ 8 caracteres, al menos una mayúscula, una minúscula, un dígito y un carácter especial. Lanza `ContraseñaNoSegura` (HTTP 400) si falla cualquier regla. Es un servicio de dominio **puro** (sin dependencias externas).
- **`UserValidationService`**: envuelve al `UserRepositoryProtocol` para centralizar la regla "si el usuario no existe, lanzar `UsuarioNoEncontrado`". Expone `obtener_usuario_existente(email)` (usado en Login) y `get_user(current_user)` (usado para obtener el perfil completo del usuario autenticado en `GET /usuarios/user/current`).

### 6.3 Aplicación — Casos de Uso (`application/use_cases/`)

#### `RegisterUseCase.register(usuario, imagen)`
Flujo: normaliza el DTO a entidad `AuthUser` (`_normalizar_registro_a_cargar`, captura `ValidationError` de Pydantic para convertir errores de longitud en `LongitudExcedida`) → valida la política de contraseñas → hashea la contraseña → si se adjuntó una imagen, delega en `ImageProtocol.insertar_imagen` → persiste el usuario vía `UserRepositoryProtocol.insertar` → genera un token de verificación (`TokenProtocol.create_access_token`) → construye la URL de verificación con `settings.BASE_URL` + `settings.NOMBRE_APP` → genera y envía el correo de bienvenida (`MailProtocol`).

#### `LoginUseCase.login(mail, password, response)`
Ver flujo detallado en la Sección 5.1. Internamente delega en dos métodos privados: `_emitir_tokens_usuario` (arma `LoginResponse`) y `_retornar_usuario_publico` (proyecta `AuthUser` → `UsuarioLogeado`, exponiendo solo `email` e `imagen_url`, nunca el hash de la contraseña).

#### `LogoutUseCase.logout(response)`
El más simple de los cinco: delega íntegramente en `CookiesService.delete_auth_cookies(response)`.

#### `RefreshTokenUseCase.refreshed_token(refresh_token, response)`
Extrae el `user_id` del refresh token (`TokenProtocol.get_user_id_from_refresh_token`), genera un nuevo access token y lo vuelve a setear como cookie (`CookiesService.set_access_cookie`). No reemite un nuevo refresh token (comportamiento de *sliding session* parcial: el refresh token original sigue vigente hasta su expiración).

#### `VerifyMailUseCase.verificar_mail(token, response)`
Decodifica el token de verificación, busca al usuario **sin filtrar por estado activo** (`obtener_por_id_sin_activar`), lo activa (`UserRepositoryProtocol.activar`, que marca `estado=ACTIVO` e `is_verified=True`) y, tras la activación, **emite inmediatamente un par de tokens de sesión** (el usuario queda logueado automáticamente al verificar su correo, sin necesidad de un login adicional).

### 6.4 Dominio — Excepciones (`domain/exceptions/`)

`DomainError` es la clase base de **toda** excepción de negocio del sistema. Contiene `message` y `status_code` (por defecto 400), y **cada subclase fija su propio `status_code` como atributo de clase**:

```python
class DomainError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code or getattr(self, "status_code", 400)
        super().__init__(self.message)
```

Jerarquías identificadas:

- **`domain.py`**: `ContraseñaNoSegura` (400), `SinCargas` (409), `LongitudExcedida` (422), `LimiteTamañoSuperado` (413), `ExtensionNoPermitida` (400), `ErrorCloudinary` (500).
- **`tokens.py`**: `TokenException` → `TokenExpirado` (403), `VerificacionExpirada` (403), `TokenInvalido` (401), `VerificacionInvalida` (401).
- **`usuarios_exceptions.py`**: `UsuarioError` (400) → `LoginError` (400), `UsuarioNoEncontrado` (409), `NoAutenticado` (401), `SinAccessToken` (401), `SinRefreshToken` (401), `TokenInvalido` (401), `UsuariosNoEncontrados` (409), `AvatarError` (409), `TiempoInterrupcionInicioSesion` (403), `UsuarioInactivo` (423); y `ResultadoInvalido` (409) como subclase directa de `DomainError`.

> **Hallazgo técnico relevante**: existen **dos clases distintas llamadas `TokenInvalido`** en módulos diferentes (`domain/exceptions/tokens.py` y `domain/exceptions/usuarios_exceptions.py`). `TokenService` (infraestructura) importa y lanza la versión de `usuarios_exceptions`, mientras que `VerifyMailUseCase` captura explícitamente la versión de `domain/exceptions/tokens.py` en su bloque `except`. Al ser clases con el mismo nombre pero de módulos distintos, **el `except TokenInvalido` de `VerifyMailUseCase` no captura la excepción realmente lanzada por `TokenService`**. El sistema sigue funcionando correctamente de cara al cliente porque ambas excepciones heredan, en última instancia, de `DomainError` y son capturadas por el manejador global (con el mismo `status_code=401`, aunque con un mensaje distinto al que el desarrollador probablemente pretendía mostrar). Se detalla como recomendación de mejora en la Sección 14.

Gracias a este diseño, el manejo de errores está completamente centralizado: **ningún router necesita un bloque `try/except` genérico** (routers.py solo captura explícitamente `VerificacionExpirada`/`VerificacionInvalida` en el endpoint de verificación, de forma redundante con el handler global, ya que ambas ya son `DomainError`).

### 6.5 Infraestructura

| Archivo | Clase / Función | Rol |
|---|---|---|
| `persistence/postgres/models.py` | `AuthUser` (tabla), `UsuarioCreado`, `UserRegisterDTO`, `UserTokens`, `UsuarioLogeado`, `LoginResponse`, `AuthUserNoImage` | Modelo de tabla + DTOs de entrada/salida, todos `SQLModel` |
| `persistence/postgres/auth_user_repository.py` | `UserRepository` | Implementación concreta de `UserRepositoryProtocol` sobre `Session` de SQLModel |
| `security/security.py` | `PasswordService`, `get_password_service` | Hash/verificación Argon2 (`pwdlib.PasswordHash.recommended()`) |
| `security/tokens/tokens.py` | `TokenService`, `get_token_service` | Codificación/decodificación JWT (`python-jose`), cálculo de expiración |
| `mail/mail.py` | `MailService`, `get_mail_service` | Renderizado Jinja2 + envío async vía `FastMail` |
| `images/cloudinary_config.py` | — | Configuración global del SDK `cloudinary` a partir de `Settings` |
| `images/cloudinary.py` | `ImageService`, `get_image_service` | Validación (tamaño ≤ 5 MB, extensiones `jpg/jpeg/png/webp`) + subida a Cloudinary |
| `templates/verificacion.html` | — | Plantilla HTML (con CSS embebido y tema oscuro) para el correo de bienvenida |

> **Observación de diseño (duplicación de factories)**: los archivos `security.py`, `tokens.py`, `mail.py` y `cloudinary.py` definen **cada uno su propia función `get_*_service(settings: Settings = Depends(get_settings))`** a nivel de módulo de infraestructura. Sin embargo, el sistema de DI efectivamente utilizado por los routers es el definido en `container/providers.py`, que declara **sus propias funciones homónimas** (`get_token_service`, `get_password_service`, `get_mail_service`, `get_image_service`) tipadas contra los Protocols. Las funciones factory locales dentro de `infrastructure/` no son importadas ni utilizadas en ningún punto del flujo activo (routers → providers → container); constituyen código muerto o, alternativamente, una capa de conveniencia pensada para uso fuera de este módulo (tests unitarios, scripts). Se recomienda documentar esta intención o eliminarlas para evitar ambigüedad (ver Sección 14).

### 6.6 Presentación (`presentation/web/`)

- **`cookies/cookies.py` — `CookiesService`**: centraliza la política de cookies. `get_cookie_settings()` decide `secure` y `samesite` **dinámicamente según `settings.is_prod`** (en desarrollo: `secure=False`, `samesite="lax"`; en producción: `secure=True`, `samesite="none"`, necesario para escenarios cross-site con `secure` obligatorio). Expone `set_auth_cookies` (access 15 min + refresh 7 días, valores *hardcodeados* en segundos en vez de leer `settings.ACCESS_TOKEN_EXPIRE_MINUTES`/`REFRESH_TOKEN_DURATION` — ver Sección 14), `set_access_cookie` y `delete_auth_cookies`.
- **`guards.py` — `AuthDependencies`**: expone `get_current_user` (decodifica el JWT de la cookie `access_token`, valida `type == "access"`, busca el usuario activo por ID), `get_admin_user` y `get_premium_user`. Estos dos últimos verifican `user.role` y `user.is_premium` respectivamente.
  > **Hallazgo técnico**: el modelo `AuthUser` (Sección 10) **no define los campos `role` ni `is_premium`**. `get_admin_user`/`get_premium_user` fallarían con `AttributeError` en tiempo de ejecución si se invocan. Estos guards funcionan como un **placeholder/extensión preparada**: la plantilla anticipa un sistema de roles/planes premium, pero requiere que el desarrollador agregue esos campos al modelo antes de usarlos (ver guía de extensión, Sección 12).
- **`routers.py`**: capa HTTP delgada. Construye el prefijo del router (`/{settings.NOMBRE_APP}/usuarios`) usando el **singleton `settings`** importado directamente del módulo `config.py` (no vía `Depends`), lo cual es necesario porque el prefijo de un `APIRouter` se define en tiempo de importación, antes de que exista un ciclo de petición HTTP donde `Depends` pueda resolverse.

---

## 7. Configuración y Variables de Entorno

Toda la configuración se centraliza en `src/config/config.py` mediante `pydantic_settings.BaseSettings`, que carga automáticamente un archivo `.env` ubicado en la raíz del proyecto (`BASE_DIR`) y **valida los tipos al arrancar la aplicación** (fail-fast: si falta una variable obligatoria, la app no arranca).

| Variable | Tipo | Obligatoria | Módulo consumidor | Propósito |
|---|---|---|---|---|
| `is_prod` | `bool` (default `False`) | No | `CookiesService` | Determina `secure`/`samesite` de las cookies |
| `DATABASE_URL` | `str` | Sí | `database/client.py` | Cadena de conexión a PostgreSQL (ej. `postgresql://usuario:tu_clave_secreta@localhost:5432/mi_db`) |
| `JWT_SECRET_KEY` | `str` | Sí | `TokenService` | Clave secreta de firma de los JWT (usar valor largo y aleatorio, ej. `tu_clave_secreta_de_al_menos_32_caracteres`) |
| `ALGORITHM` | `str` | Sí | `TokenService` | Algoritmo de firma JWT (ej. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | Sí | `TokenService` | Duración del access token en minutos |
| `REFRESH_TOKEN_DURATION` | `int` | Sí | `TokenService` | Duración del refresh token en días |
| `MAIL_USERNAME` | `str` | Sí | `MailService` | Usuario SMTP |
| `MAIL_PASSWORD` | `str` | Sí | `MailService` | Contraseña/clave de aplicación SMTP (ej. `tu_clave_secreta`) |
| `MAIL_FROM` | `str` | Sí | `MailService` | Dirección remitente |
| `MAIL_PORT` | `int` | Sí | `MailService` | Puerto SMTP (587/465) |
| `MAIL_SERVER` | `str` | Sí | `MailService` | Host SMTP |
| `MAIL_STARTTLS` | `bool` (default `True`) | No | `MailService` | Habilita STARTTLS |
| `MAIL_SSL_TLS` | `bool` (default `False`) | No | `MailService` | Habilita SSL/TLS directo |
| `USE_CREDENTIALS` | `bool` (default `True`) | No | `MailService` | Si el SMTP requiere autenticación |
| `NOMBRE_APP` | `str` | Sí | `routers.py`, `MailService`, `RegisterUseCase` | Nombre lógico de la app; usado como prefijo de rutas, carpeta de Cloudinary y branding del correo |
| `BASE_URL` | `str` | Sí | `RegisterUseCase` | URL base pública usada para construir el link de verificación |
| `CLOUDINARY_CLOUD_NAME` | `str` | Sí | `cloudinary_config.py` | Identificador de la cuenta Cloudinary |
| `CLOUDINARY_API_KEY` | `str` | Sí | `cloudinary_config.py` | Clave pública de API (ej. `tu_clave_publica`) |
| `CLOUDINARY_API_SECRET` | `str` | Sí | `cloudinary_config.py` | Clave privada de API (ej. `tu_clave_secreta`) |
| `CLOUDINARY_UPLOAD_PRESET` | `str` | Sí | `ImageService` | Preset de subida configurado en el panel de Cloudinary |

`model_config` usa `extra="ignore"`, por lo que variables adicionales en el `.env` no declaradas en `Settings` se ignoran silenciosamente en vez de fallar — útil para entornos compartidos con otras herramientas, pero puede ocultar errores tipográficos en nombres de variables.

---

## 8. Guía de Instalación, Configuración y Ejecución

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd <carpeta-del-proyecto>

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear el archivo .env en la raíz del proyecto (mismo nivel que /src)
#    Completar con valores propios (ver Sección 7). Ejemplo mínimo:
cat <<'EOF' > .env
is_prod=False
DATABASE_URL=postgresql://usuario:tu_clave_secreta@localhost:5432/auth_db
JWT_SECRET_KEY=tu_clave_secreta_larga_y_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_DURATION=7
MAIL_USERNAME=usuario@ejemplo.com
MAIL_PASSWORD=tu_clave_secreta
MAIL_FROM=usuario@ejemplo.com
MAIL_PORT=587
MAIL_SERVER=smtp.ejemplo.com
NOMBRE_APP=mi_app
BASE_URL=http://localhost:8000
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_clave_publica
CLOUDINARY_API_SECRET=tu_clave_secreta
CLOUDINARY_UPLOAD_PRESET=usuarios
EOF

# 6. Asegurarse de que la base de datos PostgreSQL exista
#    (créala manualmente con tu gestor preferido, p. ej.: createdb auth_db)

# 7. Levantar el servidor de desarrollo
uvicorn src.main:app --reload
```

Tras el arranque:
- Documentación interactiva: `http://localhost:8000/docs` (Swagger) y `http://localhost:8000/redoc`.
- Las tablas se crean automáticamente al iniciar la app mediante `SQLModel.metadata.create_all(engine)` en `main.py` — **no requiere migraciones para el arranque inicial** (ver nota sobre Alembic en la Sección 10).

---

## 9. Subsistema de Autenticación, Autorización y Seguridad

### 9.1 Registro

1. `POST /{NOMBRE_APP}/usuarios/registrar` recibe `multipart/form-data` (`email`, `password`, `imagen` opcional), parseado por `parse_usuario_form` (Sección 6, `dtos.py`) hacia un `UserRegisterDTO`.
2. `RegisterUseCase` normaliza el email (`strip().lower()`) y valida longitudes vía Pydantic (`AuthUser(**datos_limpios)`).
3. `PasswordPolicyService.validar()` exige ≥ 8 caracteres, mayúscula, minúscula, dígito y símbolo — de lo contrario `ContraseñaNoSegura` (400).
4. La contraseña se hashea con **Argon2** (`PasswordProtocol.hash_password`) **antes** de tocar la base de datos; el texto plano nunca se persiste ni se loguea.
5. Si se adjuntó imagen, se sube a Cloudinary (validación de tamaño ≤ 5 MB y extensión `jpg/jpeg/png/webp` ocurre **antes** de la llamada de red al proveedor).
6. El usuario se inserta con `estado=PENDIENTE` e `is_verified=False` (valores por defecto del modelo `AuthUser`).
7. Se genera un token de verificación con `TokenProtocol.create_access_token(user_id)` — **reutiliza el mismo mecanismo y tipo (`"type": "access"`) que un access token de sesión normal**.
8. Se construye la URL: `{BASE_URL}/{NOMBRE_APP}/usuarios/verificar/{token}` y se envía por correo (plantilla `verificacion.html`).

> **Hallazgo técnico relevante**: la plantilla `verificacion.html` muestra al usuario el texto *"El enlace expira en 24 horas"*, pero el token de verificación en realidad expira según `ACCESS_TOKEN_EXPIRE_MINUTES` (pensado para sesiones cortas, típicamente 15–30 minutos). Existe una **discrepancia entre el mensaje mostrado al usuario final y el comportamiento real del sistema**: si `ACCESS_TOKEN_EXPIRE_MINUTES` está configurado con un valor bajo, el enlace de verificación caducará mucho antes de las 24 horas anunciadas. Se recomienda como mejora crear un token de propósito específico (`create_verification_token`) con una duración propia e independiente del access token de sesión.

### 9.2 Verificación de email

`GET /{NOMBRE_APP}/usuarios/verificar/{token}` → `VerifyMailUseCase.verificar_mail`: decodifica el token, recupera el usuario **sin filtrar por estado** (necesario porque el usuario aún no está `ACTIVO`), lo activa (`estado=ACTIVO`, `is_verified=True`) y **emite automáticamente un nuevo par access/refresh token**, dejando al usuario logueado inmediatamente tras verificar su correo (sin login manual adicional).

### 9.3 Login

`POST /{NOMBRE_APP}/usuarios/login` usa el esquema estándar `OAuth2PasswordRequestForm` (campo `username` mapeado al email). `UserValidationService` solo encuentra usuarios con `estado=ACTIVO` — un usuario no verificado no puede iniciar sesión (recibirá `UsuarioNoEncontrado`, 409, en lugar de un mensaje que revele que el email existe pero está pendiente de verificación; esto es una decisión de seguridad razonable para no filtrar existencia de cuentas). La verificación de contraseña se hace en tiempo constante gracias al mecanismo interno de Argon2 (`pwdlib`), mitigando ataques de temporización.

### 9.4 Ciclo de vida de los tokens JWT

| Token | Claim `type` | Duración | Dónde se genera | Dónde se transporta |
|---|---|---|---|---|
| Access Token | `"access"` | `ACCESS_TOKEN_EXPIRE_MINUTES` (config) — cookie fijada a 15 min hardcodeado (ver 9.5) | `create_access_token` | Cookie `access_token` (`HttpOnly`) |
| Refresh Token | `"refresh"` | `REFRESH_TOKEN_DURATION` días (config) — cookie fijada a 7 días hardcodeado (ver 9.5) | `create_refresh_token` | Cookie `refresh_token` (`HttpOnly`) |

Ambos se firman con `JWT_SECRET_KEY` y `ALGORITHM` mediante `python-jose`. `decode_token` centraliza la decodificación y traduce cualquier `JWTError` (incluida la expiración) a `TokenInvalido` (de `usuarios_exceptions`, no de `domain/exceptions/tokens.py` — ver Sección 6.4). `get_user_id_from_access_token` valida además que el claim `type == "access"`, evitando que un refresh token sea usado indebidamente como credencial de sesión.

### 9.5 Cookies de sesión

`CookiesService.get_cookie_settings()` fija `httponly=True` siempre (protección contra robo de token vía XSS) y ajusta `secure`/`samesite` según el entorno (`is_prod`). 

> **Nota**: los `max_age` de las cookies (`15 * 60` segundos y `7 * 24 * 60 * 60` segundos) están **hardcodeados** en `set_auth_cookies`/`set_access_cookie`, en lugar de derivarse de `settings.ACCESS_TOKEN_EXPIRE_MINUTES`/`settings.REFRESH_TOKEN_DURATION`. Si un desarrollador cambia esas variables de entorno esperando modificar la duración de sesión, **la validez del JWT cambiará pero la cookie podría expirar en el navegador antes o después que el token**, generando comportamientos inconsistentes. Se recomienda unificar ambos valores desde `Settings` (ver Sección 12/14).

### 9.6 Renovación de sesión (Refresh)

`POST /{NOMBRE_APP}/usuarios/Refresh/Token` lee la cookie `refresh_token` (no requiere `Authorization` header), valida el token y emite un nuevo access token, sin reemitir un nuevo refresh token — el usuario debe volver a autenticarse por completo cuando el refresh token expire.

### 9.7 Logout

`POST /{NOMBRE_APP}/usuarios/Logout` simplemente borra ambas cookies del lado del servidor (`response.delete_cookie`). Como los JWT son *stateless*, **no existe invalidación real del token en el servidor** (no hay blacklist/Redis): si el token fue exfiltrado antes del logout, seguirá siendo técnicamente válido hasta su expiración natural — comportamiento estándar de JWT sin estado, y un punto de extensión razonable si se requiere revocación inmediata (ver Sección 12).

### 9.8 Autorización basada en Guards

`get_current_user` (usado en `GET /usuarios/user/current`) es el único guard actualmente cableado a un endpoint. `get_admin_user`/`get_premium_user` están definidos y listos para usarse en nuevos endpoints, aunque requieren extender el modelo `AuthUser` (ver Sección 6.6 y 12).

---

## 10. Capa de Persistencia y Modelos de Datos

### 10.1 Motor de base de datos

`database/client.py` crea un **único engine SQLModel/SQLAlchemy** a partir de `settings.DATABASE_URL` (`echo=False`, sin `connect_args` adicionales). `get_session()` es un **generador** (`with Session(engine) as session: yield session`) usado como `Depends(get_session)`, garantizando que la sesión se abra y cierre correctamente en el ciclo de vida de cada petición HTTP (una sesión por request, cerrada automáticamente al finalizar, incluso ante excepción, gracias al `with`).

### 10.2 Creación de esquema y migraciones

`main.py` ejecuta `SQLModel.metadata.create_all(engine)` al arrancar la aplicación, creando las tablas si no existen. `alembic==1.18.4` está declarado en `requirements.txt`, pero **no existe carpeta `alembic/` ni `alembic.ini` en el repositorio actual** — es decir, el sistema de migraciones versionadas está previsto en el stack pero aún no configurado. Actualmente, cualquier cambio de esquema requiere recrear la base de datos o migrar manualmente. Se recomienda inicializar Alembic (`alembic init alembic`) antes de evolucionar el modelo en un entorno con datos reales (ver Sección 12).

### 10.3 Modelo `AuthUser` (tabla `auth_users`)

```python
class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"
    id_usuario: Optional[int]            # PK autoincremental
    email: str                            # único, indexado
    password: str                         # hash Argon2 (nunca texto plano)
    imagen_url: Optional[str]             # URL pública de Cloudinary
    imagen_public_id: Optional[str]       # ID interno para reemplazo/borrado en Cloudinary
    estado: Optional[EstadoEntidad]       # default PENDIENTE (enum a nivel de columna SQL)
    created_at: Optional[date]            # server_default CURRENT_DATE
    updated_at: Optional[date]            # server_default CURRENT_DATE
    is_verified: bool                     # default False
```

`estado` se mapea a un **tipo ENUM nativo de PostgreSQL** (`estado_entidad`) vía `sqlalchemy.types.Enum`, con `server_default` en el propio motor de base de datos — una decisión robusta que garantiza integridad incluso ante inserciones fuera de la aplicación.

### 10.4 Enum `EstadoEntidad`

```python
class EstadoEntidad(str, Enum):
    ACTIVO = 'activo'
    ELIMINADO = 'eliminado'
    REPORTADO = 'reportado'
    SUSPENDIDO = 'suspendido'
    PENDIENTE = 'pendiente'
```

Definido en `database/enums/` (no en `auth/`), lo que sugiere que está pensado como un **enum transversal**, reutilizable por futuras entidades más allá de usuarios (ver Sección 12).

### 10.5 DTOs adicionales en `models.py`

| Clase | Propósito |
|---|---|
| `UsuarioCreado` | Respuesta pública del endpoint de registro (no expone `password`) |
| `UserRegisterDTO` | Entrada normalizada para `RegisterUseCase` |
| `UserTokens` | Par access/refresh + `token_type` fijo `"bearer"` |
| `UsuarioLogeado` | Proyección pública del usuario dentro de `LoginResponse` (`email`, `imagen_url`) |
| `LoginResponse` | Combina `UserTokens` + `UsuarioLogeado` |
| `AuthUserNoImage` | DTO con `email` (máx. 55) + `password`; no está referenciado por ningún Caso de Uso ni router actual — probablemente un modelo preparado para un flujo de registro sin imagen o para tests, no integrado todavía |

### 10.6 Repositorio (`UserRepository`)

Implementa `UserRepositoryProtocol` de forma **estructural** (sin heredar explícitamente del `Protocol`, cumpliendo el contrato solo por firma de métodos — el mecanismo real de Python `Protocol`). Usa `session.exec(select(...))` (API de SQLModel) en lugar de `session.query()` (API legacy de SQLAlchemy 1.x), alineado con las buenas prácticas de SQLModel/SQLAlchemy 2.0. `insertar()` captura `IntegrityError` (por ejemplo, email duplicado) y hace `rollback()` explícito antes de re-lanzar, evitando dejar la sesión en un estado inconsistente. `obtener_por_email` y `obtener_por_id` **filtran doblemente** por `estado == ACTIVO`, mientras que `obtener_por_id_sin_activar` intencionalmente no filtra (necesario durante el flujo de verificación de email, cuando el usuario aún no está activo).

---

## 11. Integración de Servicios Externos

### 11.1 Cloudinary (almacenamiento de imágenes)

- **`cloudinary_config.py`** configura el SDK globalmente al importar el módulo (`cloudinary.config(...)`), leyendo credenciales desde `Settings`.
- **`ImageService.subir_imagen()`** valida `servicio` contra una lista blanca (`SERVICIOS_VALIDOS = ["usuarios", "example_1"]`), valida tamaño (`MAX_FILE_SIZE = 5 MB`) y extensión antes de invocar `cloudinary_uploader.upload(...)`, organizando los archivos en Cloudinary bajo la carpeta `{NOMBRE_APP}/{servicio}`. Cualquier excepción del SDK se envuelve en `ErrorCloudinary` (500), evitando que detalles internos del proveedor se filtren sin control al cliente.
- **`ImageService.insertar_imagen()`** es el método expuesto a través de `ImageProtocol`; internamente delega en `subir_imagen()` y actualiza `objeto.imagen_url`/`objeto.imagen_public_id`. Este método fue diseñado deliberadamente para **recibir el `UploadFile` como parámetro explícito** (en vez de que la clase lo gestione internamente desde el request), lo que mantiene a `ImageService` agnóstico de cómo se obtuvo el archivo, favoreciendo su testeo con archivos simulados.

  > Nota de nomenclatura: `subir_imagen` es un método **público** en la implementación actual, mientras que el docstring del protocolo (`ImageProtocol`) sugiere en su ejemplo de referencia que el detalle de subida debería exponerse como `_subir_imagen` (privado), dejando `insertar_imagen` como único método público del contrato. Formalizar `subir_imagen` como `_subir_imagen` reforzaría la encapsulación ya buscada en el diseño (Sección 13).

### 11.2 FastAPI-Mail + Jinja2 (correo electrónico)

- **`MailService`** configura `ConnectionConfig` a partir de `Settings` en el constructor y crea una instancia de `FastMail` reutilizable durante la vida de la instancia.
- **`generar_correo_verificacion(url, nombre_proyecto)`** carga `verificacion.html` con `jinja2.Environment(loader=FileSystemLoader(TEMPLATE_DIR))` y renderiza las variables `url_verificacion` y `nombre_app`.
- **`enviar_mail()`** es `async` (I/O de red) y delega en `fast_mail.send_message()`; el asunto se enriquece automáticamente con el nombre de la app (`f"{asunto} - {self.settings.NOMBRE_APP}"`).
- La plantilla `verificacion.html` es completamente autocontenida (CSS embebido, sin dependencias externas salvo una fuente de íconos vía CDN), con diseño responsive y tema oscuro.

---

## 12. Guía del Desarrollador: Cómo extender la plantilla

Esta sección presenta los pasos **exactos** para extender el proyecto sin romper la arquitectura existente.

### 12.1 Agregar un nuevo endpoint a un módulo existente

1. Si el endpoint requiere nueva lógica de negocio, crear primero el Caso de Uso correspondiente (ver 12.2).
2. En `presentation/web/routers.py`, agregar la función del endpoint usando `@router.get/post/...`, inyectando el Caso de Uso vía `Depends(get_mi_nuevo_use_case)`.
3. El endpoint **no debe contener lógica de negocio** — solo extraer parámetros HTTP, llamar al Caso de Uso y mapear excepciones/errores HTTP específicos si el manejador global no es suficiente.

### 12.2 Agregar un nuevo Caso de Uso

1. Crear el archivo en `application/use_cases/mi_caso_de_uso.py`.
2. La clase debe recibir **únicamente Protocolos y Servicios de Dominio** en su constructor (nunca clases concretas de `infrastructure/`):
   ```python
   class MiCasoDeUso:
       def __init__(self, repository: UserRepositoryProtocol, token_service: TokenProtocol):
           self.repository = repository
           self.token_service = token_service

       def ejecutar(self, ...):
           ...
   ```
3. En `container/auth_container.py`, crear una clase `ContainerMiCasoDeUso` con una propiedad que construya e instancie el caso de uso.
4. En `container/providers.py`, crear `get_mi_caso_de_uso(...)` que resuelva las dependencias vía `Depends()` y delegue en el `Container` correspondiente.
5. Inyectar `get_mi_caso_de_uso` en el router (paso 12.1).

### 12.3 Agregar una nueva entidad/modelo

1. Definir el modelo `SQLModel` (`table=True`) en `infrastructure/persistence/postgres/models.py` (o un nuevo archivo bajo `persistence/postgres/` si el dominio es distinto de usuarios).
2. Si la entidad necesita estados, reutilizar `EstadoEntidad` (`database/enums/estado_entidad.py`) si aplica semánticamente, o crear un nuevo enum en la misma carpeta siguiendo el mismo patrón (`class MiEnum(str, Enum)`).
3. Definir DTOs de entrada/salida específicos (siguiendo el patrón `UsuarioCreado`/`UserRegisterDTO`) para no exponer el modelo de tabla completo (que incluye campos sensibles) directamente en las respuestas HTTP.
4. Como no hay Alembic configurado aún (Sección 10.2), inicializarlo antes de introducir cambios de esquema en una base de datos con datos reales; en desarrollo, `SQLModel.metadata.create_all()` creará la tabla automáticamente al reiniciar la app.

### 12.4 Implementar un nuevo repositorio o servicio (cambiar de proveedor)

Este es el flujo que más beneficio obtiene de la arquitectura actual:

1. Localizar el `Protocol` correspondiente en `domain/protocols/` (por ejemplo, `ImageProtocol` para migrar de Cloudinary a AWS S3).
2. Crear una nueva clase en `infrastructure/` (por ejemplo, `infrastructure/images/s3.py :: S3ImageService`) que implemente **exactamente la misma firma de métodos** descrita en el docstring del protocolo. No es necesario heredar de la clase `Protocol` explícitamente (cumplimiento estructural).
3. En `container/providers.py`, modificar **una sola función**:
   ```python
   def get_image_service(settings: Settings = Depends(get_settings)) -> ImageProtocol:
       return S3ImageService(settings)   # antes: ImageService(settings)  (Cloudinary)
   ```
4. Ningún archivo de `domain/` ni `application/` requiere modificación — es la prueba práctica de que el DIP se cumple.

### 12.5 Agregar autorización basada en roles (completar `get_admin_user`)

1. Agregar los campos faltantes al modelo `AuthUser` (Sección 6.6): `role: str = Field(default="user")` y/o `is_premium: bool = Field(default=False)`.
2. Los guards `get_admin_user`/`get_premium_user` en `guards.py` ya están implementados y funcionarán sin cambios adicionales una vez el modelo tenga esos campos.
3. Proteger un endpoint reemplazando `Depends(get_current_user)` por `Depends(get_admin_user)` o `Depends(get_premium_user)`.

---

## 13. Buenas Prácticas y Patrones de Diseño Aplicados

### 13.1 Principios SOLID — evidencia directa en el código

**Single Responsibility Principle (SRP)**
Cada Caso de Uso resuelve exactamente un flujo (`LogoutUseCase` solo borra cookies; `RefreshTokenUseCase` solo renueva el access token). `CookiesService` solo gestiona cookies; `PasswordPolicyService` solo valida reglas de contraseña. Ninguna clase mezcla persistencia, seguridad y HTTP en un mismo método.

**Open/Closed Principle (OCP)**
La jerarquía `DomainError` permite agregar nuevas excepciones de negocio (por ejemplo, `AvatarError`, `TiempoInterrupcionInicioSesion`) sin modificar el manejador global en `main.py`, que opera genéricamente sobre `exc.status_code` y `exc.message`. Del mismo modo, agregar un nuevo proveedor de imágenes (Sección 12.4) no requiere modificar `RegisterUseCase`.

**Liskov Substitution Principle (LSP)**
Cualquier clase que cumpla `TokenProtocol` puede sustituir a `TokenService` en `LoginUseCase`, `RegisterUseCase`, `VerifyMailUseCase` y `RefreshTokenUseCase` sin alterar su comportamiento esperado por el llamador, porque los Casos de Uso solo invocan los métodos definidos en el contrato, sin asumir detalles de JWT.

**Interface Segregation Principle (ISP)**
Los protocolos están segmentados por responsabilidad concreta (`PasswordProtocol` con solo 2 métodos, `MailProtocol` con solo 2 métodos) en lugar de un único "ServiceProtocol" gigante. Un Caso de Uso que solo necesita hashear contraseñas (ninguno actualmente, pero sería el caso de un futuro `ChangePasswordUseCase`) dependería únicamente de `PasswordProtocol`, sin arrastrar métodos de tokens o correo que no usa.

**Dependency Inversion Principle (DIP)** — el pilar central del proyecto
```python
# application/use_cases/login.py — depende de PROTOCOLOS, no de implementaciones
class LoginUseCase:
    def __init__(
        self,
        auth_user_repository: UserRepositoryProtocol,   # ← abstracción
        password_service: PasswordProtocol,          # ← abstracción
        token_service: TokenProtocol,                 # ← abstracción
        ...
    ):
```
La clase de alto nivel (`LoginUseCase`) y la de bajo nivel (`TokenService`, con JWT concreto) dependen ambas de la abstracción `TokenProtocol`; ninguna depende directamente de la otra.

### 13.2 Otros patrones de diseño identificados

- **Repository Pattern**: `UserRepository` encapsula toda la consulta SQL, dejando a la capa de aplicación libre de sentencias `select`/`session.exec`.
- **Dependency Injection (vía FastAPI `Depends`)**: sin frameworks externos de DI; el propio sistema de `Depends` de FastAPI resuelve el grafo completo de dependencias por petición.
- **Composition Root**: `container/` es el único punto donde Protocolos e implementaciones concretas se encuentran, siguiendo el patrón formalizado por Mark Seemann para sistemas con DI manual.
- **DTO (Data Transfer Object)**: `UserRegisterDTO`, `UsuarioLogeado`, `UsuarioCreado` desacoplan la representación pública de la entidad interna (`AuthUser`), evitando fugas de campos sensibles (`password`) en las respuestas HTTP.
- **Global Exception Handler (Chain of Responsibility simplificado)**: un único `@app.exception_handler(DomainError)` reemplaza decenas de bloques `try/except` repetidos en cada endpoint.

### 13.3 DRY y KISS

- **DRY**: la lógica de expiración/codificación JWT está centralizada en `_encode_token`/`_obtener_tiempo_expiracion` (métodos privados de `TokenService`), evitando duplicar la construcción del payload en `create_access_token`/`create_refresh_token`.
- **KISS**: `LogoutUseCase` es deliberadamente trivial (una sola línea de lógica real), evitando sobre-ingeniería en un flujo que no lo requiere.

---

## 14. Resumen y Conclusiones Técnicas

### 14.1 Evaluación de robustez y mantenibilidad

El proyecto demuestra una aplicación **coherente y madura** de Clean Architecture sobre FastAPI, con una separación de capas que se sostiene en la práctica (no solo en la teoría): el dominio efectivamente no conoce infraestructura, la infraestructura efectivamente cumple los protocolos del dominio, y el "cableado" final ocurre en un único punto controlado (`container/`). El manejo de errores mediante una jerarquía única de `DomainError` con `status_code` propio por excepción es una solución elegante que elimina repetición y mantiene consistencia en las respuestas HTTP. El uso de `Protocol` en lugar de `ABC` es una elección moderna y pragmática de Python que evita acoplar las implementaciones a una jerarquía de herencia rígida.

### 14.2 Escalabilidad como plantilla reutilizable

El diseño cumple su objetivo declarado: **cambiar de proveedor externo (Cloudinary → S3, Argon2 → Bcrypt, FastAPI-Mail → SendGrid) requiere tocar exactamente un archivo** (`container/providers.py`), sin propagar cambios a `domain/` ni `application/`. Esto valida la inversión de dependencias como estrategia real de extensibilidad, no solo como ejercicio académico.

### 14.3 Áreas de mejora detectadas durante la auditoría

Estos hallazgos no comprometen el funcionamiento actual del sistema (los flujos principales de registro, login, verificación y refresh operan correctamente extremo a extremo), pero se documentan como oportunidades de refinamiento para el mantenedor del proyecto:

1. **Colisión de nombres de excepción `TokenInvalido`** entre `domain/exceptions/tokens.py` y `domain/exceptions/usuarios_exceptions.py` (Sección 6.4), que hace que el bloque `except TokenInvalido` de `VerifyMailUseCase` no capture la excepción efectivamente lanzada por `TokenService`. Recomendación: unificar en una única jerarquía de excepciones de token.
2. **Discrepancia entre la duración anunciada del enlace de verificación** ("24 horas" en la plantilla HTML) **y su duración real**, gobernada por `ACCESS_TOKEN_EXPIRE_MINUTES` (Sección 9.1). Recomendación: introducir un método `create_verification_token` con expiración propia e independiente del access token de sesión.
3. **`max_age` de las cookies hardcodeado** en `CookiesService` en lugar de derivarse de `settings.ACCESS_TOKEN_EXPIRE_MINUTES`/`REFRESH_TOKEN_DURATION` (Sección 9.5), lo que puede desincronizar la vida útil de la cookie respecto a la del JWT que contiene.
4. **Guards `get_admin_user`/`get_premium_user`** referencian campos (`role`, `is_premium`) ausentes en el modelo `AuthUser` actual (Sección 6.6); están preparados como extensión, pero fallarían si se invocan sin antes completar el modelo.
5. **Funciones factory duplicadas** (`get_password_service`, `get_token_service`, `get_mail_service`, `get_image_service`) definidas tanto dentro de `infrastructure/` como en `container/providers.py`, donde solo esta última cadena es la efectivamente utilizada por los routers (Sección 6.5).
6. **Ausencia de configuración activa de Alembic** pese a estar en `requirements.txt` (Sección 10.2); el esquema actual se crea vía `create_all()`, adecuado para desarrollo pero no recomendable como única estrategia una vez el proyecto tenga datos de producción.
7. **Sin invalidación server-side de tokens** en logout (Sección 9.7) — comportamiento esperado en JWT *stateless*, pero a considerar si se requiere revocación inmediata (por ejemplo, mediante una blacklist en Redis).

### 14.4 Conclusión general

En conjunto, esta plantilla constituye una base **sólida, didáctica y genuinamente reutilizable** para iniciar proyectos backend con FastAPI que requieran autenticación robusta desde el primer commit. Su mayor fortaleza es arquitectónica: la combinación de Protocolos de Python, Casos de Uso desacoplados y un Composition Root explícito logra, en la práctica, lo que Clean Architecture promete en la teoría. Los hallazgos señalados en 14.3 son ajustes puntuales y de bajo riesgo, no defectos estructurales, y su resolución fortalecerá aún más la coherencia entre el diseño y el comportamiento observable del sistema.