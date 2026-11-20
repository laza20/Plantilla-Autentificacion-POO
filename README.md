# auth-core — Núcleo de Autenticación FastAPI (Clean Architecture + SOLID)

> **Versión del paquete:** 1.4.0 · **Python:** >= 3.11 · **Nombre del paquete:** `auth-core` · **Import:** `auth_core`

## 1. Introducción y Objetivo General

Este repositorio es un **núcleo de autenticación, autorización y ciclo de vida de cuenta** construido con **FastAPI** y **PostgreSQL**, diseñado explícitamente para ser **reutilizado entre múltiples proyectos/clientes**, en lugar de ser una solución de un solo uso.

Desde la versión 1.4.0 el núcleo puede usarse de **dos formas**:

1. **Como paquete instalable con `pip`** (`auth-core`): el proyecto cliente lo declara como dependencia y lo importa como `auth_core.*`, igual que cualquier librería. El código del núcleo queda en `site-packages` y no aparece dentro del proyecto cliente.
2. **Como plantilla de partida (uso híbrido)**: se clona el repositorio para copiar *una sola vez* los archivos de arranque (`main.py` de ejemplo, `alembic.ini`, `env.py`, `.env.example`, `.gitignore`) al proyecto nuevo. El núcleo igualmente se **instala**, no se copia (ver Sección 8.3).

El objetivo técnico central es demostrar cómo se puede construir un módulo de autenticación **completo** — registro, verificación por correo, login, gestión de sesiones multi-dispositivo, recuperación de contraseña, modificación de perfil, eliminación de cuenta (soft delete) y reactivación — **sin acoplar la lógica de negocio al framework ni a proveedores externos concretos**. Esto se logra aplicando **Clean Architecture**, los principios **SOLID** y, en particular, el **Principio de Inversión de Dependencias (DIP)** implementado mediante `typing.Protocol` de Python (contratos estructurales en lugar de herencia de `ABC`).

En términos prácticos:

- Los **Casos de Uso** (`RegisterUseCase`, `LoginUseCase`, `EliminarUsuarioUseCase`, etc.) no saben si las contraseñas se hashean con Argon2 o Bcrypt, si los correos se envían con FastAPI-Mail o SendGrid, o si las imágenes viven en Cloudinary o S3. Solo conocen **protocolos**.
- Cambiar de proveedor implica crear una clase que cumpla el protocolo correspondiente y modificar **una sola función** en el contenedor de dependencias.
- Toda operación que modifica más de una tabla se ejecuta dentro de una **Unidad de Trabajo** (`UnitOfWorkProtocol`) con commit/rollback atómico.
- **El esquema de base de datos lo gestiona exclusivamente Alembic**: la aplicación no crea tablas al arrancar.

Esta plantilla cubre el ciclo de vida completo de una cuenta: **alta → verificación → uso → recuperación de contraseña → baja (reversible) → reactivación**.

> **Estado del release (no es parte de la documentación funcional):** al momento de esta actualización el cambio de lectura del `.env` estaba sin commitear y el tag `v1.4.0` existía solo en local, apuntando a un commit anterior a ese cambio. Pendiente: commit, mover el tag, merge a `main`, push y probar la instalación desde GitHub. Hasta entonces, la línea de instalación de la Sección 8.2 está marcada **A VERIFICAR**.

---

## 2. Características Principales y Stack Tecnológico

### Características principales

- **Distribución como paquete instalable** (`pyproject.toml`, setuptools, layout `src/`): un único paquete de primer nivel, `auth_core`, con las plantillas HTML incluidas.
- Registro de usuarios con **imagen de perfil opcional** vía `multipart/form-data`.
- **Verificación de cuenta por correo** con plantilla HTML (Jinja2) y token JWT de scope propio (`type: "verification"`).
- **Reenvío del correo de verificación** para cuentas `PENDIENTE`.
- **Login** con `OAuth2PasswordRequestForm`, registrando IP y User-Agent del dispositivo.
- **JWT de doble token** (access + refresh) como **cookies `HttpOnly`**.
- **Sesiones multi-dispositivo**: tabla `sesiones` con hash del refresh token, IP y User-Agent; listado (marcando la sesión actual) y revocación puntual.
- **Renovación de sesión** (`/Refresh/Token`) y **Logout** que invalida la sesión también del lado del servidor.
- **Recuperación de contraseña en tres pasos** con token opaco hasheado en BD y JWT `reset` en cookie de `path` restringido.
- **Historial de contraseñas** (`history_password`) dentro de la misma transacción del cambio.
- **Modificación de perfil** (email y/o imagen), reactivando la verificación si el email cambia.
- **Eliminación de cuenta (soft delete)** con confirmación por correo y revocación de todas las sesiones.
- **Reactivación de cuenta** dentro de una ventana configurable, confirmada por correo.
- **Rate limiting por endpoint** con `slowapi` (activable/desactivable con `RATE_LIMITER_ENABLED`).
- **Migraciones con Alembic** (migración inicial `crear tablas de auth` incluida; viven en el proyecto, no en el paquete).
- **Hashing Argon2** (`pwdlib`), políticas de contraseña y de mail como servicios de dominio.
- **Subida de imágenes a Cloudinary** con validación de tamaño y extensión.
- **Manejo de errores centralizado** (`DomainError` → respuesta HTTP vía `exception_handler` global y el mapa `HTTP_STATUS_BY_EXCEPTION`).
- **Guards** (`get_current_user`, `get_admin_user`, `get_premium_user`) para proteger endpoints.
- **DI 100% vía FastAPI `Depends`**.
- **Suite de tests** (171 tests: unitarios con fakes/stubs y tests de routers con overrides) — ver Sección 4.1.

### Dependencias

Las dependencias del paquete se declaran en `pyproject.toml` con **rangos mínimos** (`>=`). `requirements.txt` se mantiene en el repositorio con versiones fijadas (útil para reproducir el entorno de desarrollo).

| Categoría | Tecnología | Rol |
|---|---|---|
| Framework web | `fastapi` | Enrutamiento, validación, DI |
| ORM / Modelado | `sqlmodel` + `SQLAlchemy` | Modelos tipados |
| Driver PostgreSQL | `psycopg2-binary` | Conexión a PostgreSQL |
| Migraciones | `alembic` | Creación y evolución del esquema |
| JWT | `python-jose` (+ `cryptography`) | Tokens de sesión y de scope (verificación, reset, eliminación, reactivación) |
| Tokens opacos | `secrets` + `hashlib` (stdlib) | Token plano de recuperación, hasheado con SHA-256 |
| Hashing de contraseñas | `pwdlib` + `argon2-cffi` | Argon2 |
| Correo | `fastapi-mail` + `aiosmtplib` | Envío SMTP asíncrono |
| Plantillas | `Jinja2` (dependencia de `fastapi-mail`) | Renderizado de las 4 plantillas HTML vía `TemplateRenderer` |
| Imágenes | `cloudinary` | Almacenamiento de imágenes |
| Rate limiting | `slowapi` | Límites de peticiones por endpoint |
| Configuración | `pydantic-settings` + `python-dotenv` | Lectura y validación del `.env` |
| Validación | `pydantic` + `email-validator` | DTOs y `EmailStr` |
| Multipart | `python-multipart` | `Form()` y `UploadFile` |
| Extra `dev` | `coverage`, `httpx`, `mypy`, `pytest`, `pytest-asyncio`, `pytest-cov`, `uvicorn` | Tests y servidor de desarrollo |

- El servidor ASGI (`uvicorn`) **no** es dependencia del paquete: está en el extra `dev`. Un proyecto cliente debe declararlo en su propio `requirements.txt`.
- `requirements.txt` aún lista `sentry-sdk` y `sqlacodegen`, que no se usan en el código y no están en `pyproject.toml`.

---

## 3. Arquitectura del Sistema

### 3.1 Patrón arquitectónico

Variante de **Clean Architecture** (cercana a Hexagonal / Ports & Adapters). Todo el núcleo vive en `src/auth_core/`:

1. **Dominio** (`auth_core/auth/domain/`): entidades (dataclasses), Protocolos como "puertos", servicios de política y excepciones.
2. **Aplicación** (`auth_core/auth/application/`): **17 Casos de Uso** organizados por sub-dominio, DTOs y mappers; reciben sus dependencias como protocolos por constructor.
3. **Infraestructura** (`auth_core/auth/infrastructure/`): modelos SQLModel, mappers modelo↔entidad, repositorios PostgreSQL, `TokenService`, `PasswordService`, `AuthMailContent`, plantillas HTML.
4. **Presentación** (`auth_core/auth/presentation/web/`): routers, guards, cookies, utilidades de formularios y metadata de la request, mapa de excepciones → HTTP.
5. **Composición** (`auth_core/container/`): Composition Root con **17 clases `Container*`** y las factories `get_*` de `providers.py`.
6. **Transversales** (fuera de `auth/`, reutilizables por futuros módulos):
   - `auth_core/database/`: engine y sesión (`client.py`), `EstadoEntidad`, `UnitOfWorkProtocol` y su implementación `UnitOfWork`.
   - `auth_core/shared/`: `ImageProtocol`/`TipadoImagenProtocol`/`MailProtocol`, `ImageService` (Cloudinary), `MailService` (FastAPI-Mail), `TemplateRenderer` (Jinja2) y el `limiter` de `slowapi`.
   - `auth_core/domain/exceptions/domain.py`: `DomainError` y excepciones genéricas.
   - `auth_core/config/config.py`: `Settings`.

### 3.2 Responsabilidad de cada capa

| Capa | Carpeta | Responsabilidad | ¿Conoce FastAPI? | ¿Conoce infraestructura concreta? |
|---|---|---|---|---|
| **Dominio** | `auth/domain/` | Entidades, contratos (Protocols), políticas, excepciones | No | No |
| **Aplicación** | `auth/application/` | Orquesta casos de uso sobre protocolos y `UnitOfWorkProtocol`; DTOs y mappers | No | No (solo protocolos) |
| **Infraestructura** | `auth/infrastructure/`, `shared/infrastructure/`, `database/repository/` | Implementaciones concretas | Sí | Sí |
| **Presentación** | `auth/presentation/web/` | Endpoints, cookies, guards | Sí | No directamente |
| **Composición** | `container/` | Ensambla implementaciones para satisfacer los protocolos | Sí (`Depends`) | Sí |

### 3.3 Reglas de dependencia y matices

```
Presentación  →  Aplicación  →  Dominio
Infraestructura  →  Dominio  (implementa los Protocols)
Composición (container)  →  conoce TODAS las capas
```

- **Repositorios y servicios**: la capa de Aplicación nunca importa un repositorio ni un servicio concreto; solo protocolos (incluido `AuthMailContentProtocol` para el contenido de los correos y `TipadoImagenProtocol` para las imágenes, sin dependencia de `fastapi`).
- **Entidades y modelos separados**: el dominio trabaja con **entidades dataclass** (`AuthUser`, `Sesion`, `RecoverPassword`, `HistoryPassword`, `Usuario`); los modelos SQLModel viven solo en infraestructura y se traducen con los mappers de `persistence/postgres/mappers/`.
- **Matices pendientes**: ver Sección 14.3 (algunos métodos de `AuthUserRepository` devuelven el modelo SQLModel en lugar de la entidad).

---

## 4. Estructura de Carpetas y Directorios

El núcleo es el único paquete de primer nivel. **Dentro de `auth_core/` la estructura interna no cambió**; lo que cambió es dónde vive todo lo demás.

```
.
├── pyproject.toml                            # Metadatos del paquete auth-core 1.4.0, dependencias y package-data
├── main.py                                   # App FastAPI de EJEMPLO (fuera del paquete)
├── alembic.ini                               # (fuera del paquete)
├── alembic/                                  # (fuera del paquete) Migraciones
│   ├── env.py                                # target_metadata = SQLModel.metadata; URL desde Settings().DATABASE_URL
│   ├── script.py.mako
│   ├── README
│   └── versions/
│       └── 0767bfec6564_crear_tablas_de_auth.py   # Migración inicial (5 tablas + ENUM estado_entidad)
├── pytest.ini                                # pythonpath = . ; testpaths = test
├── requirements.txt
├── guia de uso/                              # (fuera del paquete)
│   ├── env_example.txt                       # Plantilla del .env
│   └── guia-plantilla-auth.html              # Guía paso a paso
├── .gitattributes
├── .gitignore
├── README.md
│
├── src/
│   └── auth_core/                            # ← ÚNICO paquete de primer nivel
│       ├── __init__.py
│       ├── auth/
│       │   ├── domain/
│       │   │   ├── entities/                 # entitie_auth_users, _sesiones, _recover_password, _history_password, _usuario
│       │   │   ├── exceptions/               # tokens.py, usuarios_exceptions.py
│       │   │   ├── protocols/
│       │   │   │   ├── repository/           # auth_user, user, sesion, recover_password, history_password
│       │   │   │   └── service/              # token, password, request_metadata, auth_mail_content
│       │   │   └── services/                 # mail_policy, password_policy, user_validation_service
│       │   ├── application/
│       │   │   ├── dtos/                     # auth_user_dto, sesiones_dto
│       │   │   ├── mappers/                  # auth_users, sesiones
│       │   │   └── use_cases/
│       │   │       ├── register.py, login.py, logout.py, refresh_token.py
│       │   │       ├── verify_email.py, reenviar_mail.py, modificar_usuario.py, obtener_usuario_actual.py
│       │   │       ├── sesiones/             # listar_sesiones.py, eliminar_sesiones.py
│       │   │       ├── recover_password/     # solicitud_recuperacion.py, verificar_token.py, recuperar_contraseña.py
│       │   │       ├── eliminar_usuario/     # solicitud_eliminar_usuario.py, eliminar_usuario.py
│       │   │       └── reactivacion_cuenta/  # solicitud_reactivacion_cuenta.py, reactivar_cuenta.py
│       │   ├── infrastructure/
│       │   │   ├── mail/auth_mail_content.py # AuthMailContent: renderiza las 4 plantillas
│       │   │   ├── persistence/postgres/
│       │   │   │   ├── mappers/              # modelo SQLModel <-> entidad
│       │   │   │   ├── models/               # auth_users, usuario, sesiones, recover_password, history_password
│       │   │   │   ├── repository/           # un repositorio por tabla
│       │   │   │   └── schemas/schemas_recepcion.py
│       │   │   ├── security/
│       │   │   │   ├── security.py           # PasswordService (Argon2)
│       │   │   │   └── tokens/tokens.py      # TokenService (JWT + token opaco)
│       │   │   └── templates/                # verificacion, recuperacion_contraseña, eliminar_cuenta, reactivar_cuenta (.html)
│       │   └── presentation/web/
│       │       ├── routers.py                # 17 endpoints
│       │       ├── guards.py                 # AuthDependencies
│       │       ├── exception_handlers.py     # HTTP_STATUS_BY_EXCEPTION + obtener_status_code
│       │       ├── cookies/cookies.py        # CookiesService
│       │       └── utils/                    # forms.py, request_metadata.py
│       ├── config/config.py                  # Settings (pydantic-settings)
│       ├── container/auth/                   # auth_container.py (17 Container*), providers.py (factories get_*)
│       ├── database/
│       │   ├── client.py                     # engine de SQLModel + get_session()
│       │   ├── enums/estado_entidad.py
│       │   ├── protocols/protocol_unit_of_work.py
│       │   └── repository/unit_of_work.py
│       ├── domain/exceptions/domain.py       # DomainError + excepciones genéricas
│       └── shared/
│           ├── protocols/                    # protocol_image_service, protocol_imagen_tipado, protocol_mail_service
│           └── infrastructure/
│               ├── images/                   # cloudinary_config.py, cloudinary.py (ImageService)
│               ├── mail/                     # mail.py (MailService), template_renderer.py
│               └── security/rate_limiter/limiter.py
│
└── test/                                     # (fuera del paquete) Suite de tests (ver 4.1)
```

### 4.1 Qué queda dentro y fuera del paquete

| Dentro de `auth_core` (se instala) | Fuera del paquete (raíz del repo) |
|---|---|
| `auth/`, `config/`, `container/`, `database/`, `domain/`, `shared/` | `pyproject.toml`, `main.py` (ejemplo), `alembic/` y `alembic.ini` |
| Las 4 plantillas `.html` (`package-data`) | `test/`, `guia de uso/`, `.gitignore`, `README.md` |

### 4.2 La carpeta `test/`

La carpeta está en la raíz del repo, fuera del paquete, y **no se incluye en el wheel**.

- `auth/unit/auth/domain/fakes/` — implementaciones **en memoria** de cada protocolo de repositorio.
- `auth/unit/auth/domain/service/` — **stubs** de servicios (token, password, mail, `AuthMailContent`, imagen, políticas, unit of work, cookies).
- `auth/unit/auth/domain/use_case/` — un archivo de test por caso de uso, más tests de `PasswordPolicyService` y `MailPolicyService`.
- `auth/unit/auth/application/mappers/` — tests del mapper `a_usuario_creado`.
- `auth/fixtures/` — clases `*TestEnvironment` que arman el grafo de dependencias fake/stub.
- `auth/factories/` — funciones que insertan datos de prueba (usuarios, sesiones, tokens de recuperación).
- `config/config.py` — `TestSettings` mínimo para los casos de uso que reciben valores de configuración.
- `auth/presentation/web/` — tests de routers con `TestClient` y `app.dependency_overrides` mediante `crear_override(stub_class, resultado=..., excepcion=...)`, y `test_exception_handlers.py`, que verifica que toda subclase de `DomainError` tenga status HTTP explícito.
- `auth/conftest.py` — desactiva el rate limiter (`RATE_LIMITER_ENABLED=false`) antes de importar la app y limpia los overrides tras cada test.
- `integration/` — reservado para tests contra BD real (archivos placeholder vacíos).

Los tests unitarios y de routers **no crean tablas**: el esquema lo crea únicamente Alembic. Los tests importan `main` desde la raíz, por lo que `pytest` debe ejecutarse desde la raíz del proyecto (`pytest.ini` define `pythonpath = .`).

---

## 5. Ciclo de Vida de una Petición

### 5.1 Caso: Login

1. `POST /{NOMBRE_APP}/usuarios/login` con `username` (email) y `password` en `application/x-www-form-urlencoded`.
2. El decorador `@limiter.limit("3/minute")` evalúa el límite de la IP antes de ejecutar el endpoint.
3. FastAPI resuelve `Depends(get_login_use_case)` → cadena de `container/auth/providers.py`: `get_auth_user_repository()`, `get_token_service()`, `get_password_service()`, `get_sesion_repository()`, `get_unit_of_work()`, `get_user_validation_service()`.
4. `ContainerLogin(...).login_use_case` construye `LoginUseCase`.
5. El router extrae IP y User-Agent con `RequestMetadata` y llama a `login_use_case.ejecutar(...)`.
6. Dentro del caso de uso:
   a. `UserValidationService.obtener_usuario_existente(email)` (solo usuarios `ACTIVO`; si no, `UsuarioNoEncontrado`).
   b. `PasswordProtocol.verify_password(...)`; si falla, `LoginError`.
   c. `TokenProtocol.create_user_tokens(user_id)` y `hash_token(refresh_token)`.
   d. Dentro de `UnitOfWorkProtocol`, `insertar_sesion(hash, id_usuario, ip, user_agent)`.
7. El router adjunta los tokens como cookies `HttpOnly` con `CookiesService.set_auth_cookies` y devuelve `LoginResponse`.
8. Cualquier `DomainError` es traducida por el handler global de `main.py` (el status sale de `obtener_status_code`); los excesos de rate limit, por el handler de `slowapi`.

### 5.2 Diagrama textual

```
Cliente HTTP
    │  POST /{NOMBRE_APP}/usuarios/login
    ▼
auth_core/auth/presentation/web/routers.py :: logearse()   ← @limiter.limit("3/minute")
    │  Depends(get_login_use_case) + RequestMetadata(request)
    ▼
auth_core/container/auth/providers.py :: get_login_use_case
    ├─ AuthUserRepository / SesionRepository / UnitOfWork   (sobre la misma Session)
    ├─ TokenService (TokenProtocol) / PasswordService (PasswordProtocol)
    └─ UserValidationService
    ▼
auth_core/container/auth/auth_container.py :: ContainerLogin.login_use_case → LoginUseCase(...)
    ▼
auth_core/auth/application/use_cases/login.py :: LoginUseCase    ← Capa de Aplicación
    ▼
PostgreSQL
    ▼
JSON (LoginResponse) + Set-Cookie: access_token / refresh_token (HttpOnly)

DomainError en cualquier capa → main.py :: domain_error_handler → JSON {"detail": message}
```

---

## 6. Análisis Detallado de Módulos y Capas

### 6.1 Protocolos

| Protocolo | Ubicación (dentro de `auth_core/`) | Implementación concreta |
|---|---|---|
| `AuthUserRepositoryProtocol` | `auth/domain/protocols/repository/` | `AuthUserRepository` |
| `UsuarioRepositoryProtocol` | idem | `UserRepository` (tabla `usuario`) |
| `TokenRepositoryProtocol` (sesiones) | idem | `SesionRepository` |
| `RecuperarContraseñaProtocol` | idem | `RecoverPasswordRepository` |
| `HistoryRepositoryProtocol` | idem | `HistoryPasswordRepository` |
| `TokenProtocol` | `auth/domain/protocols/service/` | `TokenService` (JWT + token opaco) |
| `PasswordProtocol` | idem | `PasswordService` (Argon2) |
| `AuthMailContentProtocol` | idem | `AuthMailContent` |
| `RequestMetadataProtocol` | idem | `RequestMetadata` |
| `UnitOfWorkProtocol` | `database/protocols/` | `UnitOfWork` (`database/repository/`) |
| `MailProtocol` (`enviar_mail`, async) | `shared/protocols/` | `MailService` |
| `ImageProtocol` (`insertar_imagen`) | `shared/protocols/` | `ImageService` (Cloudinary) |
| `TipadoImagenProtocol` (`filename`, `size`, `file`) | `shared/protocols/` | Cualquier objeto con esos atributos (p. ej. `UploadFile`) |

`TokenProtocol` es el más grande: el sistema emite **seis tipos de JWT** distinguidos por el claim `type` (`access`, `refresh`, `verification`, `reset`, `eliminacion`, `reactivacion`), cada uno con su método de creación/decodificación y su excepción de "token inactivo".

### 6.2 Dominio — Servicios

- **`PasswordPolicyService.validar`**: ≥ 8 caracteres, mayúscula, minúscula, dígito y carácter especial → `ContraseñaNoSegura` (400).
- **`MailPolicyService.validar`**: un único `@`, punto posterior con separación y ≥ 6 caracteres → `MailNoValido` (400). Usado por registro, modificación, reenvío y solicitud de reactivación.
- **`UserValidationService`**: `obtener_usuario_existente(email)` (usado en el login).

### 6.3 Aplicación — Casos de Uso

**Alta de cuenta**
- `RegisterUseCase`: normaliza, valida mail y contraseña, hashea, sube imagen (opcional), inserta en `auth_users` y `usuario` en una misma unidad de trabajo, genera token de verificación y envía el correo.
- `VerifyMailUseCase`: decodifica el token, activa la cuenta (`ACTIVO`, `is_verified=True`) y emite un par de tokens de sesión.
- `ReenviarMailUseCase`: reenvía el correo de verificación a cuentas `PENDIENTE`.

**Sesión y perfil**
- `LoginUseCase`, `LogoutUseCase` (elimina la sesión por hash del refresh token), `RefreshTokenUseCase` (emite nuevo access token).
- `ObtenerUsuarioActualUseCase`: devuelve el `UsuarioCreado` del usuario autenticado.
- `ModificarUsuarioUseCase`: email y/o imagen; si cambia el email revalida, pasa a `PENDIENTE` y reenvía la verificación.

**Sesiones multi-dispositivo**
- `ListarSesionesUseCase` (marca `es_actual` por IP) y `EliminarSesionesUseCase` (filtra por `id_usuario` para no revocar sesiones ajenas).

**Recuperación de contraseña (3 pasos)**
- `SolicitudRecuperacionUseCase`: token plano aleatorio, invalida tokens previos, persiste el hash con expiración y envía el enlace.
- `VerificarTokenUseCase`: hashea, valida vigencia y emite el JWT `reset`.
- `RecuperarContraseñaUseCase`: en una única unidad de trabajo inserta el hash anterior en `history_password`, actualiza la contraseña y desactiva el token; si algo falla lanza `ErrorCreacion`, `UsuarioNoModificado` o `TokenNoDesactivado` y revierte todo.

**Baja y reactivación**
- `SolicitudEliminacionUsuarioUseCase` → `EliminarUsuarioUseCase` (soft delete: `ELIMINADO`, `eliminado_en=hoy`, revoca todas las sesiones).
- `EnviarMailReactivacionUseCase` → `ReactivarUsuarioUseCase` (valida que esté `ELIMINADO` y dentro de la ventana `REACTIVACION_CUENTA`; si no, `UsuarioNoEliminado` / `PeriodoReactivacionFinalizado`).

### 6.4 Excepciones

`DomainError` (`auth_core/domain/exceptions/domain.py`) es la base de toda excepción de negocio y expone `message`. **El status HTTP no vive en la excepción**: lo resuelve `HTTP_STATUS_BY_EXCEPTION` en `presentation/web/exception_handlers.py`, recorriendo el MRO de la excepción (una subclase sin entrada propia hereda el status de su padre). `main.py` lo aplica en el handler global.

- **`domain/exceptions/domain.py`** (genéricas): `SinCargas` (409), `LongitudExcedida` (422), `LimiteTamañoSuperado` (413), `ExtensionNoPermitida` (400), `ErrorCloudinary` (500), `ErrorCreacion` (409), `ErrorEliminacion` (409); `DomainError` base: 500.
- **`auth/domain/exceptions/tokens.py`**: `TokenException` (400 por defecto) → `TokenExpirado`, `VerificacionExpirada` (403); `TokenNoDesactivado`, `TokenNoVerificado` (409); `TokenInvalido`, `TokenResetInactivo`, `TokenVerificacionInactivo`, `TokenReactivacionInactivo`, `TokenEliminacionInactivo`, `VerificacionInvalida`, `SinAccessToken`, `SinRefreshToken`, `SinResetToken` (401).
- **`auth/domain/exceptions/usuarios_exceptions.py`**: `UsuarioError` (400 por defecto) → `LoginError` (401), `NoAutenticado` (401), `ContraseñaNoSegura`, `MailNoValido`, `UsuarioActivo` (400), `UsuarioNoModificado`, `UsuarioNoEliminado`, `PeriodoReactivacionFinalizado`, `MailRepetido`, `UsuarioNoEncontrado`, `UsuariosNoEncontrados` (409).

Los routers no necesitan `try/except`: el handler global traduce todo `DomainError`. El test `test_exception_handlers.py` falla si aparece una excepción de dominio nueva sin status explícito.

### 6.5 Infraestructura

| Archivo (dentro de `auth_core/`) | Clase / Función | Rol |
|---|---|---|
| `auth/infrastructure/persistence/postgres/models/*.py` | `AuthUser`, `Usuario`, `Sesiones`, `RecoverPassword`, `HistoryPassword` | Modelos de tabla SQLModel |
| `.../postgres/mappers/*.py` | `a_entidad` / `a_modelo` | Traducción modelo ↔ entidad de dominio |
| `.../postgres/repository/*.py` | `AuthUserRepository`, `UserRepository`, `SesionRepository`, `RecoverPasswordRepository`, `HistoryPasswordRepository` | Implementaciones de los protocolos de repositorio |
| `database/repository/unit_of_work.py` | `UnitOfWork` | `commit()` al salir del `with` sin excepción, `rollback()` si se propaga una |
| `auth/infrastructure/security/security.py` | `PasswordService` | Argon2 |
| `auth/infrastructure/security/tokens/tokens.py` | `TokenService` | Seis tipos de JWT + token opaco y hash SHA-256 |
| `auth/infrastructure/mail/auth_mail_content.py` | `AuthMailContent` | Renderiza `verificacion`, `recuperacion_contraseña`, `eliminar_cuenta` y `reactivar_cuenta` usando `TemplateRenderer` |
| `shared/infrastructure/mail/mail.py` | `MailService` | Envío async con FastMail (solo transporte) |
| `shared/infrastructure/mail/template_renderer.py` | `TemplateRenderer` | Wrapper de `jinja2.Environment` sobre un directorio de plantillas |
| `shared/infrastructure/images/cloudinary.py` | `ImageService` | Valida tamaño (≤ 5 MB) y extensión (`jpg/jpeg/png/webp`) y sube a Cloudinary |
| `shared/infrastructure/security/rate_limiter/limiter.py` | `limiter` | `slowapi.Limiter` por IP, habilitado según `RATE_LIMITER_ENABLED` |
| `auth/infrastructure/templates/*.html` | — | Cuatro plantillas (tema oscuro, CSS embebido), empaquetadas en el wheel |

`TEMPLATES_DIR` se calcula en `auth_mail_content.py` relativo al propio archivo, por lo que las plantillas se encuentran tanto en desarrollo como con el paquete instalado.

### 6.6 Presentación

- **`CookiesService`**: `httponly=True` siempre; `secure`/`samesite` según `is_prod`. `set_auth_cookies` (access 15 min, refresh 7 días, hardcodeados), `set_access_cookie`, `delete_auth_cookies` y `set_reset_cookie` (con `path` restringido a `PATCH /modificar/password` y `max_age` derivado de `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES`).
- **`RequestMetadata`**: IP desde `X-Forwarded-For` (o `request.client.host`) y User-Agent.
- **`AuthDependencies`**: `get_current_user` devuelve un `UsuarioCreado` (valida `type == "access"`); `get_admin_user`/`get_premium_user` lanzan `NotImplementedError` hasta que exista el campo `role`.
- **`routers.py`**: 17 endpoints delgados. El prefijo `/{NOMBRE_APP}/usuarios` se construye con el singleton `settings`.

---

## 7. Configuración y Variables de Entorno

`auth_core/config/config.py` (`pydantic_settings.BaseSettings`) lee el **`.env` del directorio de trabajo** (`env_file=".env"`) y valida tipos al arrancar. **Punto de partida recomendado:** `guia de uso/env_example.txt` (copiarlo a `.env` en la raíz del proyecto).

> **Importante:** como el `.env` se busca en el directorio de trabajo, `uvicorn`, `pytest` y `alembic` deben ejecutarse **desde la raíz del proyecto**, donde está el `.env`. Las constantes `BASE_DIR` y `ENV_PATH` fueron eliminadas.

| Variable | Tipo | Obligatoria | Consumidor | Propósito |
|---|---|---|---|---|
| `is_prod` | `bool` (default `False`) | No | `CookiesService` | `secure`/`samesite` de las cookies |
| `DATABASE_URL` | `str` | Sí | `database/client.py`, `alembic/env.py` | Conexión a PostgreSQL (ej. `postgresql+psycopg2://user:pass@localhost:5432/db`) |
| `JWT_SECRET_KEY` | `str` | Sí | `TokenService` | Clave de firma de los JWT |
| `ALGORITHM` | `str` | Sí | `TokenService` | Algoritmo JWT (ej. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | Sí | `TokenService` | Duración del access token (min) |
| `REFRESH_TOKEN_DURATION` | `int` | Sí | `TokenService` | Duración del refresh token (días) |
| `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES` | `int` | Sí | `TokenService`, `CookiesService` | JWT `reset` y cookie `reset_token` |
| `VERIFY_MAIL_RECUPERACION` | `int` | Sí | `TokenService`, `SolicitudRecuperacionUseCase` | Minutos de validez del token de verificación **y** del token de recuperación |
| `EXPIRACION_MAIL_RECUPERACION` | `int` | Sí | — | Declarada, no consumida |
| `ELIMINACION_CUENTA` | `int` | Sí | `TokenService` | Minutos de validez del token de eliminación |
| `REACTIVACION_CUENTA` | `int` | Sí | `TokenService`, `ReactivarUsuarioUseCase` | Minutos de validez del JWT de reactivación **y** días de ventana post-baja |
| `MAIL_USERNAME` / `MAIL_PASSWORD` / `MAIL_FROM` / `MAIL_PORT` / `MAIL_SERVER` | `str`/`int` | Sí | `MailService` | SMTP |
| `MAIL_STARTTLS` / `MAIL_SSL_TLS` / `USE_CREDENTIALS` | `bool` | No | `MailService` | Conexión SMTP |
| `NOMBRE_APP` | `str` | Sí | routers, `MailService`, casos de uso | Prefijo de rutas, carpeta de Cloudinary, branding |
| `BASE_URL` | `str` | Sí | casos de uso con correo | Base de los enlaces enviados por mail |
| `CLOUDINARY_CLOUD_NAME` / `_API_KEY` / `_API_SECRET` / `_UPLOAD_PRESET` | `str` | Sí | `ImageService` | Cloudinary |
| `RATE_LIMITER_ENABLED` | `bool` (default `True`) | No | `limiter` | Habilita o deshabilita el rate limiting (los tests lo fijan en `false`) |

`extra="ignore"`: variables no declaradas se ignoran silenciosamente.

---

## 8. Instalación, Uso como Paquete y Ejecución

Hay tres escenarios. En todos, `uvicorn`, `pytest` y `alembic` se ejecutan desde la raíz del proyecto.

### 8.1 Desarrollo del núcleo (este repositorio)

```bash
git clone <url-del-repositorio> auth-core
cd auth-core

python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1

pip install -e .                  # instala auth-core en modo editable dentro del venv
pip install -e ".[dev]"           # opcional: pytest, httpx, uvicorn, mypy, etc.

cp "guia de uso/env_example.txt" .env     # Windows: Copy-Item ".\guia de uso\env_example.txt" ".env"
# Editar .env (DATABASE_URL, JWT_SECRET_KEY, SMTP, Cloudinary, NOMBRE_APP, BASE_URL...)

pytest -q                         # 171 passed — no tocan la base de datos

psql -U postgres -c "CREATE DATABASE mi_base;"
alembic upgrade head              # obligatorio antes de levantar el servidor
alembic current                   # debe mostrar 0767bfec6564 (head)

uvicorn main:app --reload         # main.py de ejemplo está en la raíz
```

- Documentación interactiva: `http://localhost:8000/docs` (Swagger) y `/redoc`.
- **La aplicación no crea tablas al arrancar.** Si aparece un error del tipo "la relación … no existe", faltó `alembic upgrade head`.
- Si `alembic upgrade head` falla con `DuplicateObject … estado_entidad`, la base no estaba vacía.
- Los cambios al núcleo se hacen **en este repositorio** y salen con un tag nuevo (ver 8.2).

### 8.2 Uso como instalable en un proyecto cliente

En el `requirements.txt` del proyecto cliente:

```
auth-core @ git+https://github.com/laza20/Plantilla-Autentificacion-POO.git@v1.4.0
```

> **A VERIFICAR:** la instalación desde el tag publicado en GitHub todavía no fue probada (el tag `v1.4.0` existía solo en local al momento de escribir esto). Tampoco consta si el repositorio es privado; **A VERIFICAR**. Si lo es, hacen falta credenciales de GitHub (token o `git+ssh`).

Qué ocurre y qué aporta cada parte:

- Lo instalado queda en `site-packages`: no aparecen archivos del núcleo dentro del proyecto cliente (igual que `fastapi`).
- El proyecto cliente **aporta**: su `main.py`, su `.env`, su `alembic.ini` y `alembic/env.py`, y sus propios modelos y routers.
- **Las migraciones de las tablas de auth NO viajan en el paquete.** El `env.py` del cliente debe importar los modelos desde `auth_core.auth.infrastructure.persistence.postgres.models` y usar `autogenerate` para generar la migración de esas tablas junto con las propias.
- El `main.py` del cliente puede partir del ejemplo de este repo: incluye el router de `auth_core.auth.presentation.web.routers`, registra el `limiter` y el handler de `RateLimitExceeded`, y el handler global de `DomainError`.
- El proyecto cliente debe declarar su propio servidor ASGI (`uvicorn`), que no es dependencia de `auth-core`.

**No editar el núcleo dentro del proyecto cliente**: un `pip install --upgrade` lo pisa. Si hace falta un cambio, va al repositorio de la plantilla y sale con un tag nuevo.

**Actualizar la versión instalada:**

1. Cambiar el tag en el `requirements.txt` del cliente (por ejemplo `@v1.4.1`).
2. Correr `pip install --upgrade -r requirements.txt`.

**Publicar una versión nueva del núcleo:** subir la versión en `pyproject.toml` **en el mismo commit que el tag**.

### 8.3 Uso híbrido (opcional)

Se puede clonar el repositorio solo para tomar los archivos de arranque y copiarlos **una sola vez** al proyecto nuevo:

- `main.py` de ejemplo, `alembic.ini`, `alembic/env.py`, `.env.example` (a partir de `guia de uso/env_example.txt`) y `.gitignore`.

El núcleo se **instala**, no se copia. Tener el núcleo copiado **y** además instalado genera dos copias y confusión sobre cuál se importa.

---

## 9. Autenticación, Autorización y Seguridad

### 9.1 Registro
`POST /{NOMBRE_APP}/usuarios/registrar` (`multipart/form-data`: `email`, `password`, `imagen` opcional). Valida políticas → hashea con Argon2 → sube imagen → inserta en `auth_users` y `usuario` (misma transacción) → token de verificación (`type: "verification"`) → correo de bienvenida.

### 9.2 Verificación de email
`GET /verificar/{token}` activa la cuenta y emite un par access/refresh (el usuario queda logueado). `POST /reenviar/mail` reenvía el correo mientras la cuenta siga `PENDIENTE`.

### 9.3 Login y sesiones
`POST /login` (`OAuth2PasswordRequestForm`, solo usuarios `ACTIVO`). `GET /listar_sesiones` marca `es_actual` por IP; `DELETE /eliminar_sesion/{id_sesion}` revoca una sesión puntual.

### 9.4 Tokens JWT

| Token | Claim `type` | Duración | Transporte |
|---|---|---|---|
| Access | `access` | `ACCESS_TOKEN_EXPIRE_MINUTES` | Cookie `access_token` (`HttpOnly`) |
| Refresh | `refresh` | `REFRESH_TOKEN_DURATION` días | Cookie `refresh_token` (`HttpOnly`) |
| Verificación | `verification` | `VERIFY_MAIL_RECUPERACION` min | Enlace por correo |
| Reset | `reset` | `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES` min | Cookie `reset_token` (`path` restringido) |
| Eliminación | `eliminacion` | `ELIMINACION_CUENTA` min | Enlace por correo |
| Reactivación | `reactivacion` | `REACTIVACION_CUENTA` min | Enlace por correo |

El token de recuperación del paso 1 **no** es JWT: es opaco (`secrets.token_urlsafe(32)`) y solo se persiste su hash SHA-256.

### 9.5 Recuperación de contraseña
1. `POST /solicitud/recuperacion` → token opaco + correo.
2. `GET /recuperar/password/{token}` → valida hash y vigencia, fija la cookie `reset_token`.
3. `PATCH /modificar/password` → con la cookie presente (si falta, `SinResetToken`, 401), cambia la contraseña en una única transacción (historial + actualización + desactivación del token).

### 9.6 Modificación de perfil
`PUT /modificar/usuario` (autenticado). Si cambia el email, la cuenta vuelve a `PENDIENTE` y se reenvía la verificación.

### 9.7 Eliminación (soft delete)
`DELETE /eliminar/usuario` (autenticado) envía el correo; `GET /eliminar/cuenta/{token}` marca `ELIMINADO`, revoca **todas** las sesiones y borra las cookies.

### 9.8 Reactivación
`GET /solicitud/reactivacion/cuenta` (recibe el email en el body — ver Sección 14.3) y `GET /reactivar/cuenta/{token}`.

### 9.9 Cookies
`httponly=True` siempre; `secure`/`samesite` según `is_prod`. `max_age` de access/refresh hardcodeado (ver Sección 14.3).

### 9.10 Refresh y Logout
`POST /Refresh/Token` emite un nuevo access token (si falta la cookie, `SinRefreshToken`, 401). `POST /Logout` elimina la sesión en BD (vía hash) y borra las cookies; también responde 401 si falta la cookie `refresh_token`. Un refresh token robado no puede reutilizarse tras el logout (el access token ya emitido vive hasta su expiración natural).

### 9.11 Rate limiting

Cada endpoint (salvo `GET /user/current`) tiene un límite por IP con `slowapi`:

| Endpoint | Límite |
|---|---|
| `POST /login`, `POST /Refresh/Token`, `DELETE /eliminar_sesion/{id}` | 3/minuto |
| `GET /listar_sesiones` | 5/minuto |
| `PUT /modificar/usuario` | 2/hora |
| `PATCH /modificar/password` | 3/hora |
| `POST /registrar`, `GET /verificar/{token}`, `POST /Logout`, `POST /solicitud/recuperacion`, `GET /recuperar/password/{token}`, `POST /reenviar/mail`, `DELETE /eliminar/usuario`, `GET /eliminar/cuenta/{token}`, `GET /solicitud/reactivacion/cuenta`, `GET /reactivar/cuenta/{token}` | 5/hora |

La clave es `get_remote_address` (IP directa del cliente). Detrás de un proxy o load balancer, todas las peticiones pueden compartir la misma IP a menos que se configure el reenvío de IP real (ver Sección 14.3). Con `RATE_LIMITER_ENABLED=false` el limitador se desactiva.

### 9.12 Guards
`get_current_user` está cableado en los endpoints autenticados y devuelve un `UsuarioCreado`. `get_admin_user`/`get_premium_user` son placeholders (`NotImplementedError`) hasta agregar `role`/`is_premium`.

---

## 10. Persistencia, Modelos y Migraciones

### 10.1 Motor de base de datos
`auth_core/database/client.py` crea el engine SQLModel/SQLAlchemy desde `settings.DATABASE_URL`; `get_session()` entrega una sesión por petición.

### 10.2 Migraciones con Alembic

- **Alembic es el único responsable del esquema.** `main.py` importa los modelos pero **no** ejecuta `create_all`.
- `alembic/env.py` toma la URL desde `Settings().DATABASE_URL` (sobrescribe `sqlalchemy.url` de `alembic.ini`), importa los modelos desde `auth_core.auth.infrastructure.persistence.postgres.models` y usa `SQLModel.metadata` como `target_metadata`.
- `alembic/` y `alembic.ini` **están fuera del paquete**: no viajan con `pip install`. Un proyecto cliente tiene su propio `alembic/` (ver 8.2).
- Migración inicial: `0767bfec6564_crear_tablas_de_auth.py` — crea el ENUM `estado_entidad` y las tablas `auth_users`, `history_password`, `recover_password`, `sesiones` y `usuario`, con sus índices y claves foráneas.

Flujo ante cualquier cambio de modelo (ver 12.7):

```bash
alembic revision --autogenerate -m "descripcion del cambio"
# Revisar el archivo generado en alembic/versions/ antes de aplicarlo
alembic upgrade head
```

> Requisito del autogenerate: los modelos de tabla deben importarse en `env.py` (vía `from src.auth_core.auth.infrastructure.persistence.postgres import models`, cuyo `__init__.py` exporta los cinco modelos). Un modelo nuevo debe agregarse a ese `__init__.py`, o Alembic no lo detectará.

### 10.3 Modelo de datos

| Tabla | Modelo | Rol |
|---|---|---|
| `auth_users` | `AuthUser` | Identidad y credenciales; incluye `estado` (ENUM), `is_verified`, `eliminado_en` |
| `usuario` | `Usuario` | Datos de negocio 1:1 con `auth_users` (mismo `id_usuario` como PK/FK), pensada para crecer sin tocar autenticación |
| `sesiones` | `Sesiones` | `hash_refresh_token`, `ip`, `user_agent`, `inicio_sesion`, `id_usuario` |
| `recover_password` | `RecoverPassword` | `token_hash`, `expira_en`, `usado`, `id_usuario` |
| `history_password` | `HistoryPassword` | `password_hash_anterior`, `fecha_cambio`, `id_usuario` |

```python
class EstadoEntidad(str, Enum):
    ACTIVO = 'activo'
    ELIMINADO = 'eliminado'
    REPORTADO = 'reportado'
    SUSPENDIDO = 'suspendido'
    PENDIENTE = 'pendiente'
```

El enum vive en `auth_core/database/enums/` (transversal a futuras entidades).

### 10.4 Entidades y DTOs
- **Entidades de dominio** (`auth/domain/entities/`): `AuthUser`, `UserTokens`, `Sesion`, `RecoverPassword`, `HistoryPassword`, `Usuario`.
- **DTOs de aplicación** (`auth/application/dtos/`): `UsuarioCreado`, `UsuarioLogeado`, `LoginResponse`, `UserRegisterDTO`, `UserModifyDTO`, `SesionVisual`, `ListaSesiones`.
- **Schemas de recepción** (`persistence/postgres/schemas/`): `SolicitudRecuperacionRequest`, `SolicitudReactivacionRequest`, `ModificarPassword`.
- **Mappers** (`application/mappers/`): `a_usuario_creado`, `a_sesion_visual`.

### 10.5 Repositorios
`AuthUserRepository` filtra por `estado == ACTIVO` en `obtener_por_email`/`obtener_por_id`, no filtra en `obtener_por_id_sin_activar`, y expone el par inverso para reactivación (`obtener_usuario_eliminado_por_mail/id`). `SesionRepository.eliminar_todas_las_sesiones_de_un_usuario` usa un `delete()` en bloque.

---

## 11. Integración de Servicios Externos

### 11.1 Cloudinary
`ImageService.subir_imagen()` valida servicio (`SERVICIOS_VALIDOS`), tamaño (`MAX_FILE_SIZE = 5 MB`; un `size` en `None` también se rechaza con `LimiteTamañoSuperado`) y extensión (un `filename` en `None` o sin extensión da `ExtensionNoPermitida`), y sube a `{NOMBRE_APP}/{servicio}`. El contrato `TipadoImagenProtocol` no depende de `fastapi`.

### 11.2 Correo (FastAPI-Mail + Jinja2)
El envío y la generación del contenido están **separados**:
- `MailService` (`shared/`) solo envía (`enviar_mail`).
- `AuthMailContent` (`auth/infrastructure/mail/`) genera el HTML de las cuatro plantillas usando `TemplateRenderer`; los casos de uso lo reciben por `AuthMailContentProtocol`.
- Las plantillas comparten el mismo sistema visual (violeta para verificación/recuperación/reactivación, rojo para eliminación).

---

## 12. Guía del Desarrollador: Cómo extender la plantilla

> Los cambios al núcleo se hacen en **este repositorio** y se publican con un tag nuevo; no se editan dentro de un proyecto cliente.

### 12.1 Agregar un endpoint
Crear el Caso de Uso, exponerlo en `routers.py` con `Depends`, sin lógica de negocio en el endpoint, y asignarle un `@limiter.limit(...)` acorde a su sensibilidad.

### 12.2 Agregar un Caso de Uso
1. Ubicarlo en el subpaquete semántico correspondiente de `auth_core/auth/application/use_cases/`.
2. El constructor recibe solo Protocolos y servicios de dominio.
3. Si toca más de una tabla, envolverlo en `with self.unit_of_work_service:`.
4. Crear `ContainerMiCasoDeUso` en `container/auth/auth_container.py` y `get_mi_caso_de_uso` en `container/auth/providers.py`.
5. Inyectarlo en el router.
6. Agregar su `*TestEnvironment` en `test/auth/fixtures/`, y sus fakes/stubs si hay protocolos nuevos.
7. Importar siempre con el prefijo `auth_core.` (nunca `src.`).

### 12.3 Agregar una entidad/modelo
Definir la entidad en `auth/domain/entities/`, el modelo en `infrastructure/persistence/postgres/models/` (**exportarlo en su `__init__.py`**), su mapper y los DTOs propios, y generar la migración (12.7).

### 12.4 Cambiar de proveedor
Localizar el `Protocol`, crear la nueva clase cumpliendo su firma y modificar una sola factory en `container/auth/providers.py`.

### 12.5 Autorización por roles
1. Agregar `role`/`is_premium` a `AuthUser` (entidad y modelo) **y generar la migración**.
2. Agregar el campo a `UsuarioCreado` y reemplazar el cuerpo de `get_admin_user`/`get_premium_user` en `guards.py`.
3. Proteger endpoints con `Depends(get_admin_user)` o `Depends(get_premium_user)`.

### 12.6 Extender el ciclo de vida de la cuenta
Replicar el patrón "solicitud por correo → confirmación con token de scope propio → efecto en `estado`": métodos `create_<scope>_token`/`get_user_id_from_<scope>_token` en `TokenProtocol`/`TokenService`, dos Casos de Uso (solicitud + confirmación) y una plantilla en `templates/` con su generador en `AuthMailContent`/`AuthMailContentProtocol`. Candidato natural: `EstadoEntidad.SUSPENDIDO`. Una plantilla nueva debe quedar cubierta por el `package-data` de `pyproject.toml` (hoy `auth/infrastructure/templates/*.html`).

### 12.7 Cambiar el esquema (migraciones)
1. Modificar o crear el modelo (y exportarlo en `models/__init__.py`).
2. `alembic revision --autogenerate -m "descripcion"`.
3. Revisar el archivo generado en `alembic/versions/`.
4. `alembic upgrade head`.

Un modelo modificado no se refleja en la base hasta generar y aplicar la migración.

### 12.8 Publicar una versión nueva
1. Subir `version` en `pyproject.toml`.
2. Commit y tag en **el mismo commit** (el tag debe apuntar al commit que contiene esa versión).
3. Push de la rama y del tag.
4. En los proyectos cliente, cambiar el tag en `requirements.txt` y correr `pip install --upgrade -r requirements.txt` (ver 8.2).

---

## 13. Buenas Prácticas y Patrones de Diseño Aplicados

### 13.1 SOLID
- **SRP**: un Caso de Uso por flujo; `CookiesService` solo cookies; `AuthMailContent` solo contenido de correo; `MailService` solo transporte.
- **OCP**: nuevas excepciones o proveedores sin tocar casos de uso; una excepción nueva solo requiere su entrada en `HTTP_STATUS_BY_EXCEPTION` (el test lo exige).
- **LSP**: fakes y stubs de test sustituyen a las implementaciones reales.
- **ISP**: protocolos angostos (`HistoryRepositoryProtocol`, `RecuperarContraseñaProtocol`, `UnitOfWorkProtocol`).
- **DIP**: los Casos de Uso dependen de abstracciones:

```python
class RecuperarContraseñaUseCase:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,
        unit_of_work_service: UnitOfWorkProtocol,
        password_service: PasswordProtocol,
        history_contraseña_repository: HistoryRepositoryProtocol,
        password_policy: PasswordPolicyService,
        auth_user_repository: AuthUserRepositoryProtocol,
    ): ...
```

### 13.2 Otros patrones
Repository, Unit of Work, Dependency Injection (`Depends`), Composition Root, DTO, Mapper, Global Exception Handler, Test Doubles estructurales (Fakes/Stubs), **Migraciones versionadas** (Alembic) y **distribución como paquete versionado** (tags + `pyproject.toml`).

---

## 14. Notas de Versión, Resumen y Pendientes

### 14.1 Notas de versión 1.4.0

**Cambios que rompen compatibilidad respecto de la estructura anterior**

- **Imports:** todo pasó de `src.algo` a `auth_core.algo` (por ejemplo, `from src.auth_core.container.auth.providers import ...`). Incluye `main.py`, los tests, `alembic/env.py` y los `patch()` de los tests.
- **`.env`:** `Settings` lo lee del **directorio de trabajo** (`env_file=".env"`). Se eliminaron `BASE_DIR` y `ENV_PATH`. `uvicorn`, `pytest` y `alembic` se ejecutan desde la raíz del proyecto.
- **`main.py` y `test/`** quedaron fuera del paquete, en la raíz del repo.
- **Comando de arranque:** `uvicorn main:app --reload` (antes `uvicorn src.main:app`).

**Cambios de comportamiento previos a esta rama (changelog 1.3.0 → 1.4.0)**

- `POST /Logout` y `PATCH /modificar/password` responden **401** si falta la cookie (`refresh_token` y `reset_token`, respectivamente).
- `SinAccessToken` y `SinRefreshToken` pasaron a ser `TokenException`, y existe `SinResetToken` (401).
- `get_current_user` devuelve `UsuarioCreado` en lugar de `AuthUser`.
- Las validaciones de imagen manejan `filename` y `size` en `None` (`ExtensionNoPermitida` y `LimiteTamañoSuperado`).
- `verificar_token` devuelve `False` si `expira_en` es `NULL`.
- Contrato de imágenes `TipadoImagenProtocol`, sin dependencia de `fastapi`.

**Verificaciones realizadas sobre el paquete**

- El wheel `auth_core-1.4.0` compila e instala en un venv limpio; `top_level.txt` contiene solo `auth_core`.
- Los 4 `.html` viajan en el wheel y `TEMPLATES_DIR` los encuentra con el paquete instalado.
- Desde un directorio sin `src/`, `import auth_core.auth.application.use_cases.register` funciona.
- Desde un directorio con un `.env` ajeno, el paquete instalado lee ese `.env`.
- Entorno de desarrollo: 171 tests pasan, `import main` no da error y `uvicorn main:app` arranca y cierra sin errores.

### 14.2 Evaluación y escalabilidad como plantilla

El proyecto conserva la separación de capas y ahora se distribuye como paquete versionado: un proyecto cliente instala el núcleo, lo actualiza cambiando un tag y aporta solo sus propios `main.py`, `.env`, migraciones, modelos y routers. El molde "solicitud por correo → token de scope propio → confirmación → efecto en `estado`" está probado en cuatro flujos. Con `shared/` y `database/` desacoplados de `auth/`, un segundo módulo de negocio puede reutilizar el limitador, el envío de correo, la subida de imágenes, la Unidad de Trabajo y el enum de estados.

### 14.3 Limitaciones / pendientes

**Resueltos respecto de la versión anterior del README**
- `DomainError(detail=...)` en `ImageService`: ahora usa `message=`.
- Instancia `FastAPI(...)` sin uso en `cloudinary.py`: eliminada.
- Fugas de la regla de dependencia: el dominio usa entidades dataclass; `AuthMailContent` entra por protocolo; `Settings` ya no se importa en los casos de uso; las excepciones ya no importan `fastapi.status` ni `ImageProtocol` usa `UploadFile`.
- Status HTTP fuera de la excepción: ahora vive en `HTTP_STATUS_BY_EXCEPTION`.



### 14.4 Conclusión general

La plantilla cubre el ciclo de vida completo de una cuenta con un compromiso arquitectónico consistente: Protocolos como frontera, Casos de Uso desacoplados, entidades separadas de los modelos, Composition Root explícito, Unidad de Trabajo transaccional, esquema versionado con Alembic y, desde 1.4.0, distribución como paquete `auth-core` instalable con `pip` o, alternativamente, uso híbrido a partir de los archivos de arranque. Los pendientes de la Sección 14.3 son en su mayoría ajustes de configuración, documentación y cierre del proceso de release.