# Auth Con POO SOLID — Plantilla de Autenticación FastAPI (Clean Architecture + SOLID)

## 1. Introducción y Objetivo General

Este repositorio es una **plantilla (boilerplate) de autenticación, autorización y ciclo de vida de cuenta** construida con **FastAPI** y **PostgreSQL**, diseñada explícitamente para ser **reutilizada entre múltiples proyectos/clientes**, en lugar de ser una solución de un solo uso.

El objetivo técnico central es demostrar cómo se puede construir un módulo de autenticación **completo** — registro, verificación por correo, login, gestión de sesiones multi-dispositivo, recuperación de contraseña, modificación de perfil, eliminación de cuenta (soft delete) y reactivación — **sin acoplar la lógica de negocio al framework ni a proveedores externos concretos**. Esto se logra aplicando **Clean Architecture**, los principios **SOLID** y, en particular, el **Principio de Inversión de Dependencias (DIP)** implementado mediante `typing.Protocol` de Python (contratos estructurales en lugar de herencia de `ABC`).

En términos prácticos:

- Los **Casos de Uso** (`RegisterUseCase`, `LoginUseCase`, `EliminarUsuarioUseCase`, etc.) no saben si las contraseñas se hashean con Argon2 o Bcrypt, si los correos se envían con FastAPI-Mail o SendGrid, o si las imágenes viven en Cloudinary o S3. Solo conocen **protocolos**.
- Cambiar de proveedor implica crear una clase que cumpla el protocolo correspondiente y modificar **una sola función** en el contenedor de dependencias.
- Toda operación que modifica más de una tabla se ejecuta dentro de una **Unidad de Trabajo** (`UnitOfWorkProtocol`) con commit/rollback atómico.
- **El esquema de base de datos lo gestiona exclusivamente Alembic**: la aplicación no crea tablas al arrancar.
- El repositorio incluye una **guía de uso paso a paso** (`guia de uso/guia-plantilla-auth.html`) y un `.env` de ejemplo para poner en marcha la plantilla en un proyecto nuevo (ver Sección 8).

Esta plantilla cubre el ciclo de vida completo de una cuenta: **alta → verificación → uso → recuperación de contraseña → baja (reversible) → reactivación**.

---

## 2. Características Principales y Stack Tecnológico

### Características principales

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
- **Migraciones con Alembic** (migración inicial `crear tablas de auth` incluida).
- **Hashing Argon2** (`pwdlib`), políticas de contraseña y de mail como servicios de dominio.
- **Subida de imágenes a Cloudinary** con validación de tamaño y extensión.
- **Manejo de errores centralizado** (`DomainError` → respuesta HTTP vía `exception_handler` global).
- **Guards** (`get_current_user`, `get_admin_user`, `get_premium_user`) para proteger endpoints.
- **DI 100% vía FastAPI `Depends`**.
- **Suite de tests** (unitarios con fakes/stubs y tests de routers con overrides) — ver Sección 4.1.

### Stack tecnológico (`requirements.txt`)

| Categoría | Tecnología | Rol |
|---|---|---|
| Framework web | `fastapi==0.136.1` | Enrutamiento, validación, DI |
| Servidor ASGI | `uvicorn==0.46.0` | Servidor de desarrollo/producción |
| ORM / Modelado | `sqlmodel==0.0.38` + `SQLAlchemy==2.0.49` | Modelos tipados |
| Driver PostgreSQL | `psycopg2-binary==2.9.12` | Conexión a PostgreSQL |
| Migraciones | `alembic==1.18.4` | Creación y evolución del esquema |
| JWT | `python-jose==3.5.0` | Tokens de sesión y de scope (verificación, reset, eliminación, reactivación) |
| Tokens opacos | `secrets` + `hashlib` (stdlib) | Token plano de recuperación, hasheado con SHA-256 |
| Hashing de contraseñas | `pwdlib==0.3.0` + `argon2-cffi==25.1.0` | Argon2 |
| Correo | `fastapi-mail==1.6.4` + `aiosmtplib==5.1.1` | Envío SMTP asíncrono |
| Plantillas | `Jinja2==3.1.6` | Renderizado de las 4 plantillas HTML vía `TemplateRenderer` |
| Imágenes | `cloudinary==1.44.2` | Almacenamiento de imágenes |
| Rate limiting | `slowapi==0.1.10` + `limits==5.8.0` | Límites de peticiones por endpoint |
| Configuración | `pydantic-settings==2.14.1` + `python-dotenv==1.2.2` | Lectura y validación del `.env` |
| Validación | `pydantic==2.13.4` + `email-validator==2.3.0` | DTOs y `EmailStr` |
| Multipart | `python-multipart==0.0.28` | `Form()` y `UploadFile` |
| Testing | `pytest==9.1.1`, `pytest-asyncio==1.4.0`, `pytest-cov==7.1.0` | Tests unitarios y de routers |
| Herramientas | `sqlacodegen==4.0.3`, `sentry-sdk==2.59.0` | Declaradas en `requirements.txt`; no se usan en el código actual |

**Lenguaje:** Python 3.10+ (uniones `str | None`, `typing.Protocol`).

---

## 3. Arquitectura del Sistema

### 3.1 Patrón arquitectónico

Variante de **Clean Architecture** (cercana a Hexagonal / Ports & Adapters):

1. **Dominio** (`src/auth/domain/`): Protocolos como "puertos", servicios de política y excepciones.
2. **Aplicación** (`src/auth/application/`): **16 Casos de Uso** organizados por sub-dominio, que reciben sus dependencias como protocolos por constructor.
3. **Infraestructura** (`src/auth/infrastructure/`): modelos, repositorios PostgreSQL, `TokenService`, `PasswordService`, `AuthMailContent`, plantillas HTML.
4. **Presentación** (`src/auth/presentation/web/`): routers, guards, cookies y metadata de la request.
5. **Composición** (`src/container/`): Composition Root con **16 clases `Container*`** y las factories `get_*` de `providers.py`.
6. **Transversales** (fuera de `auth/`, reutilizables por futuros módulos):
   - `src/database/`: engine y sesión (`client.py`), `EstadoEntidad`, `UnitOfWorkProtocol` y su implementación `UnitOfWork`.
   - `src/shared/`: `ImageProtocol`/`MailProtocol`, `ImageService` (Cloudinary), `MailService` (FastAPI-Mail), `TemplateRenderer` (Jinja2) y el `limiter` de `slowapi`.
   - `src/domain/exceptions/domain.py`: `DomainError` y excepciones genéricas.
   - `src/config/config.py`: `Settings`.

### 3.2 Responsabilidad de cada capa

| Capa | Carpeta | Responsabilidad | ¿Conoce FastAPI? | ¿Conoce infraestructura concreta? |
|---|---|---|---|---|
| **Dominio** | `auth/domain/` | Contratos (Protocols), políticas, excepciones | Parcialmente (ver 3.3) | Solo modelos/DTOs (ver 3.3) |
| **Aplicación** | `auth/application/` | Orquesta casos de uso sobre protocolos y `UnitOfWorkProtocol` | Parcialmente (`UploadFile`) | Modelos/DTOs, `AuthMailContent` y `Settings`; nunca repositorios ni servicios concretos |
| **Infraestructura** | `auth/infrastructure/`, `shared/infrastructure/`, `database/repository/` | Implementaciones concretas | Sí | Sí |
| **Presentación** | `auth/presentation/web/` | Endpoints, cookies, guards | Sí | No directamente |
| **Composición** | `container/` | Ensambla implementaciones para satisfacer los protocolos | Sí (`Depends`) | Sí |

### 3.3 Reglas de dependencia y matices

```
Presentación  →  Aplicación  →  Dominio
Infraestructura  →  Dominio  (implementa los Protocols)
Composición (container)  →  conoce TODAS las capas
```

Matices honestos sobre el cumplimiento de la regla:

- **Repositorios y servicios**: la capa de Aplicación nunca importa un repositorio ni un servicio concreto (`AuthUserRepository`, `TokenService`, `PasswordService`, `MailService`, `ImageService`); solo protocolos.
- **Modelos y DTOs**: los protocolos de dominio y los Casos de Uso importan modelos SQLModel (`AuthUser`, `Sesiones`, `UserTokens`, `LoginResponse`…) desde `infrastructure/persistence/`. Es una fuga aceptada de la plantilla: los modelos hacen de entidad y de DTO a la vez.
- **Otras fugas puntuales**: `AuthMailContent` (infraestructura) es inyectado por tipo concreto en los Casos de Uso que envían correos; `Settings` se importa desde `infrastructure/security/security.py` en algunos casos de uso; `domain/exceptions/*.py` importa `fastapi.status`, e `ImageProtocol` usa `fastapi.UploadFile`.

---

## 4. Estructura de Carpetas y Directorios

```
.
├── .gitattributes                            # Fuerza EOL=LF en *.py, *.ini, *.mako
├── .gitignore
├── alembic.ini
├── pytest.ini                                # pythonpath = . ; testpaths = src/test
├── README.md
├── requirements.txt
│
├── alembic/                                  # Migraciones
│   ├── env.py                                # target_metadata = SQLModel.metadata; URL desde Settings().DATABASE_URL
│   ├── script.py.mako
│   ├── README
│   └── versions/
│       └── 0767bfec6564_crear_tablas_de_auth.py   # Migración inicial (5 tablas + ENUM estado_entidad)
│
├── guia de uso/                              # Documentación operativa para proyectos nuevos
│   ├── env_example.txt                       # Plantilla del .env
│   └── guia-plantilla-auth.html              # Guía paso a paso (clonar, vincular, entorno, BD, Alembic, servidor)
│
└── src/
    ├── main.py                               # App FastAPI, router, rate limiter y exception handler global (NO crea tablas)
    │
    ├── config/
    │   └── config.py                         # Settings (pydantic-settings) — lee y valida el .env
    │
    ├── container/                            # Composition Root
    │   ├── auth_container.py                 # 16 clases "Container*" — una por caso de uso
    │   └── providers.py                      # Factories get_* usadas como Depends()
    │
    ├── database/
    │   ├── client.py                         # engine de SQLModel + get_session()
    │   ├── enums/estado_entidad.py           # EstadoEntidad
    │   ├── protocols/protocol_unit_of_work.py  # UnitOfWorkProtocol
    │   └── repository/unit_of_work.py        # UnitOfWork (commit/rollback sobre Session)
    │
    ├── domain/exceptions/domain.py           # DomainError + excepciones genéricas
    │
    ├── shared/                               # Servicios reutilizables entre módulos
    │   ├── protocols/
    │   │   ├── protocol_image_service.py     # ImageProtocol
    │   │   └── protocol_mail_service.py      # MailProtocol
    │   └── infrastructure/
    │       ├── images/
    │       │   ├── cloudinary_config.py
    │       │   └── cloudinary.py             # ImageService
    │       ├── mail/
    │       │   ├── mail.py                   # MailService (FastAPI-Mail)
    │       │   └── template_renderer.py      # TemplateRenderer (Jinja2)
    │       └── security/rate_limiter/limiter.py   # Limiter de slowapi
    │
    ├── auth/
    │   ├── domain/
    │   │   ├── protocols/
    │   │   │   ├── repository/
    │   │   │   │   ├── protocol_auth_user_repository.py
    │   │   │   │   ├── protocol_user_repository.py
    │   │   │   │   ├── protocol_sesion_repository.py
    │   │   │   │   ├── protocol_recover_password_repository.py
    │   │   │   │   └── protocol_history_password_repository.py
    │   │   │   └── service/
    │   │   │       ├── protocol_token_service.py
    │   │   │       ├── protocol_password_service.py
    │   │   │       └── protocol_request_metadata.py
    │   │   ├── services/                     # password_policy, mail_policy, user_validation_service
    │   │   └── exceptions/                   # tokens.py, usuarios_exceptions.py
    │   │
    │   ├── application/
    │   │   ├── dtos.py                       # parse_usuario_form, parse_modificar_usuario_form
    │   │   └── use_cases/
    │   │       ├── register.py, login.py, logout.py, refresh_token.py
    │   │       ├── verify_email.py, reenviar_mail.py, modificar_usuario.py
    │   │       ├── sesiones/                 # listar_sesiones.py, eliminar_sesiones.py
    │   │       ├── recover_password/         # solicitud_recuperacion.py, verificar_token.py, recuperar_contraseña.py
    │   │       ├── eliminar_usuario/         # solicitud_eliminar_usuario.py, eliminar_usuario.py
    │   │       └── reactivacion_cuenta/      # solicitud_reactivacion_cuenta.py, reactivar_cuenta.py
    │   │
    │   ├── infrastructure/
    │   │   ├── mail/auth_mail_content.py     # AuthMailContent: renderiza las 4 plantillas
    │   │   ├── persistence/postgres/
    │   │   │   ├── models/                   # auth_users, usuario, sesiones, recover_password, history_password
    │   │   │   ├── repository/               # un repositorio por tabla
    │   │   │   └── schemas/schemas_recepcion.py
    │   │   ├── security/
    │   │   │   ├── security.py               # PasswordService (Argon2)
    │   │   │   └── tokens/tokens.py          # TokenService (JWT + token opaco)
    │   │   └── templates/                    # verificacion, recuperacion_contraseña, eliminar_cuenta, reactivar_cuenta (.html)
    │   │
    │   └── presentation/web/
    │       ├── routers.py                    # 17 endpoints
    │       ├── guards.py                     # AuthDependencies
    │       ├── cookies/cookies.py            # CookiesService
    │       └── utils/request_metadata.py     # RequestMetadata
    │
    └── test/                                 # Suite de tests (ver 4.1)
        ├── conftest.py                       # RATE_LIMITER_ENABLED=false, test_client, limpieza de overrides
        ├── config/config.py                  # TestSettings
        ├── factories/                        # usuarios, sesiones, recover_password
        ├── fixtures/                         # *TestEnvironment por caso de uso
        ├── integration/                      # Reservado (placeholders vacíos)
        ├── presentation/web/                 # overrides/, stub/, routers/
        └── unit/auth/domain/                 # fakes/, service/ (stubs), use_case/
```

### 4.1 La carpeta `test/`

- `unit/auth/domain/fakes/` — implementaciones **en memoria** de cada protocolo de repositorio.
- `unit/auth/domain/service/` — **stubs** de servicios (token, password, mail, `AuthMailContent`, imagen, políticas, unit of work, cookies).
- `unit/auth/domain/use_case/` — un archivo de test por caso de uso, más tests de `PasswordPolicyService` y `MailPolicyService`.
- `fixtures/` — clases `*TestEnvironment` que arman el grafo de dependencias fake/stub.
- `factories/` — funciones que insertan datos de prueba (usuarios, sesiones, tokens de recuperación).
- `config/config.py` — `TestSettings` mínimo para los casos de uso que reciben `Settings`.
- `presentation/web/` — tests de routers con `TestClient` y `app.dependency_overrides` mediante `crear_override(stub_class, resultado=..., excepcion=...)`.
- `conftest.py` — desactiva el rate limiter (`RATE_LIMITER_ENABLED=false`) antes de importar la app y limpia los overrides tras cada test.
- `integration/` — reservado para tests contra BD real (archivos placeholder vacíos).

Los tests unitarios y de routers **no necesitan PostgreSQL, Cloudinary ni SMTP**, ni crean tablas: el esquema lo crea únicamente Alembic.

---

## 5. Ciclo de Vida de una Petición

### 5.1 Caso: Login

1. `POST /{NOMBRE_APP}/usuarios/login` con `username` (email) y `password` en `application/x-www-form-urlencoded`.
2. El decorador `@limiter.limit("3/minute")` evalúa el límite de la IP antes de ejecutar el endpoint.
3. FastAPI resuelve `Depends(get_login_use_case)` → cadena de `providers.py`: `get_auth_user_repository()`, `get_token_service()`, `get_password_service()`, `get_sesion_repository()`, `get_unit_of_work()`, `get_user_validation_service()`.
4. `ContainerLogin(...).login_use_case` construye `LoginUseCase`.
5. El router extrae IP y User-Agent con `RequestMetadata` y llama a `login_use_case.ejecutar(...)`.
6. Dentro del caso de uso:
   a. `UserValidationService.obtener_usuario_existente(email)` (solo usuarios `ACTIVO`; si no, `UsuarioNoEncontrado`).
   b. `PasswordProtocol.verify_password(...)`; si falla, `LoginError`.
   c. `TokenProtocol.create_user_tokens(user_id)` y `hash_token(refresh_token)`.
   d. Dentro de `UnitOfWorkProtocol`, `insertar_sesion(hash, id_usuario, ip, user_agent)`.
7. El router adjunta los tokens como cookies `HttpOnly` con `CookiesService.set_auth_cookies` y devuelve `LoginResponse`.
8. Cualquier `DomainError` es traducida por el handler global de `main.py`; los excesos de rate limit por el handler de `slowapi`.

### 5.2 Diagrama textual

```
Cliente HTTP
    │  POST /{NOMBRE_APP}/usuarios/login
    ▼
presentation/web/routers.py :: logearse()      ← @limiter.limit("3/minute")
    │  Depends(get_login_use_case) + RequestMetadata(request)
    ▼
container/providers.py :: get_login_use_case
    ├─ AuthUserRepository / SesionRepository / UnitOfWork   (sobre la misma Session)
    ├─ TokenService (TokenProtocol) / PasswordService (PasswordProtocol)
    └─ UserValidationService
    ▼
container/auth_container.py :: ContainerLogin.login_use_case → LoginUseCase(...)
    ▼
application/use_cases/login.py :: LoginUseCase        ← Capa de Aplicación
    ▼
PostgreSQL
    ▼
JSON (LoginResponse) + Set-Cookie: access_token / refresh_token (HttpOnly)

DomainError en cualquier capa → main.py :: domain_error_handler → JSON {"detail": message}
```

---

## 6. Análisis Detallado de Módulos y Capas

### 6.1 Protocolos

| Protocolo | Ubicación | Implementación concreta |
|---|---|---|
| `AuthUserRepositoryProtocol` | `auth/domain/protocols/repository/` | `AuthUserRepository` |
| `UsuarioRepositoryProtocol` | idem | `UserRepository` (tabla `usuario`) |
| `TokenRepositoryProtocol` (sesiones) | idem | `SesionRepository` |
| `RecuperarContraseñaProtocol` | idem | `RecoverPasswordRepository` |
| `HistoryRepositoryProtocol` | idem | `HistoryPasswordRepository` |
| `TokenProtocol` | `auth/domain/protocols/service/` | `TokenService` (JWT + token opaco) |
| `PasswordProtocol` | idem | `PasswordService` (Argon2) |
| `RequestMetadataProtocol` | idem | `RequestMetadata` |
| `UnitOfWorkProtocol` | `database/protocols/` | `UnitOfWork` (`database/repository/`) |
| `MailProtocol` (`enviar_mail`, async) | `shared/protocols/` | `MailService` |
| `ImageProtocol` (`insertar_imagen`) | `shared/protocols/` | `ImageService` (Cloudinary) |

`TokenProtocol` es el más grande: el sistema emite **seis tipos de JWT** distinguidos por el claim `type` (`access`, `refresh`, `verification`, `reset`, `eliminacion`, `reactivacion`), cada uno con su método de creación/decodificación y su excepción de "token inactivo".

> El docstring de `MailProtocol` aún menciona `generar_correo_verificacion`, pero ese método ya no forma parte del contrato: la generación del HTML pasó a `AuthMailContent` (ver 6.5). El protocolo solo exige `enviar_mail`.

### 6.2 Dominio — Servicios

- **`PasswordPolicyService.validar`**: ≥ 8 caracteres, mayúscula, minúscula, dígito y carácter especial → `ContraseñaNoSegura` (400).
- **`MailPolicyService.validar`**: un único `@`, punto posterior con separación y ≥ 6 caracteres → `MailNoValido` (400). Usado por registro, modificación, reenvío y solicitud de reactivación.
- **`UserValidationService`**: `obtener_usuario_existente(email)` (login) y `get_user(current_user)` (perfil).

### 6.3 Aplicación — Casos de Uso

**Alta de cuenta**
- `RegisterUseCase`: normaliza, valida mail y contraseña, hashea, sube imagen (opcional), inserta en `auth_users` y `usuario` en una misma unidad de trabajo, genera token de verificación y envía el correo.
- `VerifyMailUseCase`: decodifica el token, activa la cuenta (`ACTIVO`, `is_verified=True`) y emite un par de tokens de sesión.
- `ReenviarMailUseCase`: reenvía el correo de verificación a cuentas `PENDIENTE`.

**Sesión y perfil**
- `LoginUseCase`, `LogoutUseCase` (elimina la sesión por hash del refresh token), `RefreshTokenUseCase` (emite nuevo access token).
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

`DomainError` (`src/domain/exceptions/domain.py`) es la base de toda excepción de negocio, con `message` y `status_code`.

- **`domain/exceptions/domain.py`** (genéricas): `SinCargas` (409), `LongitudExcedida` (422), `LimiteTamañoSuperado` (413), `ExtensionNoPermitida` (400), `ErrorCloudinary` (500), `ErrorCreacion` (409), `ErrorEliminacion` (409).
- **`auth/domain/exceptions/tokens.py`**: `TokenException` → `TokenExpirado`, `VerificacionExpirada` (403), `TokenNoDesactivado`, `TokenNoVerificado` (409), `TokenInvalido`, `TokenResetInactivo`, `TokenVerificacionInactivo`, `TokenReactivacionInactivo`, `TokenEliminacionInactivo`, `VerificacionInvalida` (401).
- **`auth/domain/exceptions/usuarios_exceptions.py`**: `UsuarioError` (400) → `LoginError`, `ContraseñaNoSegura`, `MailNoValido`, `UsuarioActivo` (400), `UsuarioNoModificado`, `UsuarioNoEliminado`, `PeriodoReactivacionFinalizado`, `MailRepetido`, `UsuarioNoEncontrado`, `UsuariosNoEncontrados`, `AvatarError` (409), `NoAutenticado`, `SinAccessToken`, `SinRefreshToken` (401), `TiempoInterrupcionInicioSesion` (403), `UsuarioInactivo` (423); más `ResultadoInvalido` (409) como subclase directa de `DomainError`.

Los routers no necesitan `try/except`: el handler global traduce todo `DomainError`. (El único router que captura explícitamente, `verificar_mail`, lo hace de forma redundante y además remapea el código a 400.)

### 6.5 Infraestructura

| Archivo | Clase / Función | Rol |
|---|---|---|
| `auth/infrastructure/persistence/postgres/models/*.py` | `AuthUser`, `Usuario`, `Sesiones`, `RecoverPassword`, `HistoryPassword` + DTOs | Modelos de tabla y proyecciones |
| `.../repository/*.py` | `AuthUserRepository`, `UserRepository`, `SesionRepository`, `RecoverPasswordRepository`, `HistoryPasswordRepository` | Implementaciones de los protocolos de repositorio |
| `database/repository/unit_of_work.py` | `UnitOfWork` | `commit()` al salir del `with` sin excepción, `rollback()` si se propaga una |
| `auth/infrastructure/security/security.py` | `PasswordService` | Argon2 |
| `auth/infrastructure/security/tokens/tokens.py` | `TokenService` | Seis tipos de JWT + token opaco y hash SHA-256 |
| `auth/infrastructure/mail/auth_mail_content.py` | `AuthMailContent` | Renderiza `verificacion`, `recuperacion_contraseña`, `eliminar_cuenta` y `reactivar_cuenta` usando `TemplateRenderer` |
| `shared/infrastructure/mail/mail.py` | `MailService` | Envío async con FastMail (solo transporte) |
| `shared/infrastructure/mail/template_renderer.py` | `TemplateRenderer` | Wrapper de `jinja2.Environment` sobre un directorio de plantillas |
| `shared/infrastructure/images/cloudinary.py` | `ImageService` | Valida tamaño (≤ 5 MB) y extensión (`jpg/jpeg/png/webp`) y sube a Cloudinary |
| `shared/infrastructure/security/rate_limiter/limiter.py` | `limiter` | `slowapi.Limiter` por IP, habilitado según `RATE_LIMITER_ENABLED` |
| `auth/infrastructure/templates/*.html` | — | Cuatro plantillas (tema oscuro, CSS embebido) |

### 6.6 Presentación

- **`CookiesService`**: `httponly=True` siempre; `secure`/`samesite` según `is_prod`. `set_auth_cookies` (access 15 min, refresh 7 días, hardcodeados), `set_access_cookie`, `delete_auth_cookies` y `set_reset_cookie` (con `path` restringido a `PATCH /modificar/password` y `max_age` derivado de `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES`).
- **`RequestMetadata`**: IP desde `X-Forwarded-For` (o `request.client.host`) y User-Agent.
- **`AuthDependencies`**: `get_current_user` (valida `type == "access"`); `get_admin_user`/`get_premium_user` lanzan `NotImplementedError` hasta que exista el campo `role`.
- **`routers.py`**: 17 endpoints delgados. El prefijo `/{NOMBRE_APP}/usuarios` se construye con el singleton `settings`.

---

## 7. Configuración y Variables de Entorno

`src/config/config.py` (`pydantic_settings.BaseSettings`) carga el `.env` de la raíz del proyecto y valida tipos al arrancar. **Punto de partida recomendado:** `guia de uso/env_example.txt` (copiarlo a `.env`).

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

## 8. Guía de Instalación, Configuración y Ejecución

Guía completa (con solución a errores frecuentes en Windows/PowerShell): **`guia de uso/guia-plantilla-auth.html`**. Resumen:

```bash
# 1. Clonar (y, si querés historial propio, borrar .git y hacer git init)
git clone <url-del-repositorio> MiNuevoProyecto
cd MiNuevoProyecto

# 2. (Opcional) apuntar a tu nuevo repositorio remoto
git remote set-url origin <URL-NUEVO-REPO>

# 3. Entorno virtual + dependencias
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Variables de entorno
cp "guia de uso/env_example.txt" .env      # Windows: Copy-Item ".\guia de uso\env_example.txt" ".env"
#    Editar .env: DATABASE_URL, JWT_SECRET_KEY (python -c "import secrets; print(secrets.token_hex(32))"),
#    credenciales SMTP, Cloudinary, NOMBRE_APP, BASE_URL...

# 5. Crear una base PostgreSQL vacía
psql -U postgres -c "CREATE DATABASE mi_nuevo_proyecto_db;"

# 6. (Opcional) Ejecutar los tests — no tocan la base de datos
pytest

# 7. Crear el esquema con Alembic (obligatorio antes de levantar el servidor)
alembic upgrade head
alembic current                   # debe mostrar 0767bfec6564 (head)

# 8. Levantar el servidor
uvicorn src.main:app --reload
```

- Documentación interactiva: `http://localhost:8000/docs` (Swagger) y `/redoc`.
- **La aplicación no crea tablas al arrancar.** Si al usar un endpoint aparece un error del tipo "la relación … no existe", faltó ejecutar `alembic upgrade head`.
- Si `alembic upgrade head` falla con `DuplicateObject … estado_entidad`, la base no estaba vacía (ver el paso 4.2 de la guía de uso).

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
3. `PATCH /modificar/password` → con la cookie presente, cambia la contraseña en una única transacción (historial + actualización + desactivación del token).

### 9.6 Modificación de perfil
`PUT /modificar/usuario` (autenticado). Si cambia el email, la cuenta vuelve a `PENDIENTE` y se reenvía la verificación.

### 9.7 Eliminación (soft delete)
`DELETE /eliminar/usuario` (autenticado) envía el correo; `GET /eliminar/cuenta/{token}` marca `ELIMINADO`, revoca **todas** las sesiones y borra las cookies.

### 9.8 Reactivación
`GET /solicitud/reactivacion/cuenta` (recibe el email en el body — ver Sección 14) y `GET /reactivar/cuenta/{token}`.

### 9.9 Cookies
`httponly=True` siempre; `secure`/`samesite` según `is_prod`. `max_age` de access/refresh hardcodeado (ver Sección 14).

### 9.10 Refresh y Logout
`POST /Refresh/Token` emite un nuevo access token. `POST /Logout` elimina la sesión en BD (vía hash) y borra las cookies, por lo que un refresh token robado no puede reutilizarse (el access token ya emitido vive hasta su expiración natural).

### 9.11 Rate limiting

Cada endpoint (salvo `GET /user/current`) tiene un límite por IP con `slowapi`:

| Endpoint | Límite |
|---|---|
| `POST /login`, `POST /Refresh/Token`, `DELETE /eliminar_sesion/{id}` | 3/minuto |
| `GET /listar_sesiones` | 5/minuto |
| `PATCH /modificar/password` | 1/hora |
| `PUT /modificar/usuario` | 2/hora |
| `POST /registrar`, `GET /verificar/{token}`, `POST /Logout`, `POST /solicitud/recuperacion`, `GET /recuperar/password/{token}`, `POST /reenviar/mail`, `DELETE /eliminar/usuario`, `GET /eliminar/cuenta/{token}`, `GET /solicitud/reactivacion/cuenta`, `GET /reactivar/cuenta/{token}` | 5/hora |

La clave es `get_remote_address` (IP directa del cliente). Detrás de un proxy o load balancer, todas las peticiones pueden compartir la misma IP a menos que se configure el reenvío de IP real (ver Sección 14). Con `RATE_LIMITER_ENABLED=false` el limitador se desactiva.

### 9.12 Guards
`get_current_user` está cableado en los endpoints autenticados. `get_admin_user`/`get_premium_user` son placeholders (`NotImplementedError`) hasta agregar `role`/`is_premium` a `AuthUser`.

---

## 10. Persistencia, Modelos y Migraciones

### 10.1 Motor de base de datos
`database/client.py` crea el engine SQLModel/SQLAlchemy desde `settings.DATABASE_URL`; `get_session()` entrega una sesión por petición.

### 10.2 Migraciones con Alembic

- **Alembic es el único responsable del esquema.** `main.py` importa los modelos (`from ...postgres.models import *`) pero **no** ejecuta `create_all`.
- `alembic/env.py` toma la URL desde `Settings().DATABASE_URL` (sobrescribe `sqlalchemy.url` de `alembic.ini`), importa los modelos y usa `SQLModel.metadata` como `target_metadata`.
- Migración inicial: `0767bfec6564_crear_tablas_de_auth.py` — crea el ENUM `estado_entidad` y las tablas `auth_users`, `history_password`, `recover_password`, `sesiones` y `usuario`, con sus índices y claves foráneas.

Flujo ante cualquier cambio de modelo (ver 12.7):

```bash
alembic revision --autogenerate -m "descripcion del cambio"
# Revisar el archivo generado en alembic/versions/ antes de aplicarlo
alembic upgrade head
```

> Requisito del autogenerate: los modelos de tabla deben importarse en `env.py` (hoy vía `from src.auth.infrastructure.persistence.postgres import models`, cuyo `__init__.py` exporta los cinco modelos). Un modelo nuevo debe agregarse a ese `__init__.py`, o Alembic no lo detectará.

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

El enum vive en `database/enums/` (transversal a futuras entidades).

### 10.4 DTOs relevantes
`UsuarioCreado`, `UserRegisterDTO`, `UserModifyDTO`, `AuthUserEmailValidation`, `UserTokens`, `UsuarioLogeado`, `LoginResponse`, `SesionesVisual`, `ListaSesiones`, `SolicitudRecuperacionRequest`, `SolicitudReactivacionRequest`, `ModificarPassword`. `AuthUserNoImage` no tiene referencias activas.

### 10.5 Repositorios
`AuthUserRepository` filtra por `estado == ACTIVO` en `obtener_por_email`/`obtener_por_id`, no filtra en `obtener_por_id_sin_activar`, y expone el par inverso para reactivación (`obtener_usuario_eliminado_por_mail/id`). `SesionRepository.eliminar_todas_las_sesiones_de_un_usuario` usa un `delete()` en bloque.

---

## 11. Integración de Servicios Externos

### 11.1 Cloudinary
`ImageService.subir_imagen()` valida servicio (`SERVICIOS_VALIDOS`), tamaño (`MAX_FILE_SIZE = 5 MB`) y extensión, y sube a `{NOMBRE_APP}/{servicio}`.

### 11.2 Correo (FastAPI-Mail + Jinja2)
El envío y la generación del contenido están **separados**:
- `MailService` (`shared/`) solo envía (`enviar_mail`).
- `AuthMailContent` (`auth/infrastructure/mail/`) genera el HTML de las cuatro plantillas usando `TemplateRenderer`, y los casos de uso reciben ambos por inyección.
- Las plantillas comparten el mismo sistema visual (violeta para verificación/recuperación/reactivación, rojo para eliminación).

---

## 12. Guía del Desarrollador: Cómo extender la plantilla

### 12.1 Agregar un endpoint
Crear el Caso de Uso, exponerlo en `routers.py` con `Depends`, sin lógica de negocio en el endpoint, y asignarle un `@limiter.limit(...)` acorde a su sensibilidad.

### 12.2 Agregar un Caso de Uso
1. Ubicarlo en el subpaquete semántico correspondiente.
2. El constructor recibe solo Protocolos y servicios de dominio.
3. Si toca más de una tabla, envolverlo en `with self.unit_of_work_service:`.
4. Crear `ContainerMiCasoDeUso` en `auth_container.py` y `get_mi_caso_de_uso` en `providers.py`.
5. Inyectarlo en el router.
6. Agregar su `*TestEnvironment` en `test/fixtures/`, y sus fakes/stubs si hay protocolos nuevos.

### 12.3 Agregar una entidad/modelo
Definir el modelo en `infrastructure/persistence/postgres/models/`, **exportarlo en su `__init__.py`**, definir DTOs propios y generar la migración (12.7).

### 12.4 Cambiar de proveedor
Localizar el `Protocol`, crear la nueva clase cumpliendo su firma y modificar una sola factory en `container/providers.py`.

### 12.5 Autorización por roles
1. Agregar `role`/`is_premium` a `AuthUser` **y generar la migración**.
2. Reemplazar el cuerpo de `get_admin_user`/`get_premium_user` en `guards.py`.
3. Proteger endpoints con `Depends(get_admin_user)` o `Depends(get_premium_user)`.

### 12.6 Extender el ciclo de vida de la cuenta
Replicar el patrón "solicitud por correo → confirmación con token de scope propio → efecto en `estado`": métodos `create_<scope>_token`/`get_user_id_from_<scope>_token` en `TokenProtocol`/`TokenService`, dos Casos de Uso (solicitud + confirmación) y una plantilla en `templates/` con su generador en `AuthMailContent`. Candidato natural: `EstadoEntidad.SUSPENDIDO`.

### 12.7 Cambiar el esquema (migraciones)
1. Modificar o crear el modelo (y exportarlo en `models/__init__.py`).
2. `alembic revision --autogenerate -m "descripcion"`.
3. Revisar el archivo generado en `alembic/versions/`.
4. `alembic upgrade head`.

Un modelo modificado no se refleja en la base hasta generar y aplicar la migración. Modificar una tabla existente probablemente implique actualizar también los DTOs y modelos de recepción (no de tabla) asociados, y sus validaciones.

---

## 13. Buenas Prácticas y Patrones de Diseño Aplicados

### 13.1 SOLID
- **SRP**: un Caso de Uso por flujo; `CookiesService` solo cookies; `AuthMailContent` solo contenido de correo; `MailService` solo transporte.
- **OCP**: nuevas excepciones o proveedores sin tocar casos de uso ni el handler global.
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
Repository, Unit of Work, Dependency Injection (`Depends`), Composition Root, DTO, Global Exception Handler, Test Doubles estructurales (Fakes/Stubs), y **Migraciones versionadas** (Alembic).

---

## 14. Resumen y Conclusiones Técnicas

### 14.1 Evaluación
El proyecto conserva la separación de capas y suma en esta iteración una mejora estructural: la **gestión del esquema pasa íntegramente a Alembic** (la app ya no crea tablas al arrancar), se extraen las piezas reutilizables a `src/database/` y `src/shared/`, y se incorpora documentación operativa (`guia de uso/`) que permite poner en marcha la plantilla en un proyecto nuevo sin conocimiento previo del repositorio.

### 14.2 Escalabilidad como plantilla
El molde "solicitud por correo → token de scope propio → confirmación → efecto en `estado`" está probado en cuatro flujos. Con `shared/` y `database/` desacoplados de `auth/`, un segundo módulo de negocio puede reutilizar el limitador, el envío de correo, la subida de imágenes, la Unidad de Trabajo y el enum de estados.

### 14.3 Áreas de mejora detectadas

**Resueltas desde la auditoría anterior**
1. Colisión de `TokenInvalido` entre módulos de excepciones.
2. Token de verificación con scope propio, independiente del access token.
3. Alembic sin configurar: ahora hay `alembic.ini`, `alembic/env.py` y migración inicial.
4. `create_all` en `main.py`: eliminado; el esquema depende solo de Alembic.

**Pendientes**
1. **`max_age` de las cookies `access_token`/`refresh_token` sigue hardcodeado** (`15 * 60` y `7 * 24 * 60 * 60`) en vez de derivarse de `ACCESS_TOKEN_EXPIRE_MINUTES`/`REFRESH_TOKEN_DURATION`; `set_reset_cookie` ya aplica el patrón correcto.
2. **Doble unidad para `REACTIVACION_CUENTA`**: minutos para el JWT de reactivación, días para la ventana post-baja. Con `30`, el enlace expira en 30 minutos pero la cuenta es reactivable 30 días. Separar en dos variables.
3. **`EXPIRACION_MAIL_RECUPERACION` no es consumida** por ningún módulo.
4. **`VERIFY_MAIL_RECUPERACION` gobierna dos flujos** (verificación de mail y recuperación de contraseña).
5. **`ImageService.subir_imagen()` construye `DomainError(detail=...)`**, pero `DomainError.__init__` espera `message`: esa rama lanzaría `TypeError`. Corregir a `DomainError(message=...)`.
6. **`GET /solicitud/reactivacion/cuenta` recibe un body**; debería ser `POST`, como `POST /solicitud/recuperacion`.
7. **Plantillas con datos que no se renderizan**: `recuperacion_contraseña.html`, `eliminar_cuenta.html` y `reactivar_cuenta.html` usan `{{ tiempo_expiracion }}`, pero `AuthMailContent` no lo pasa (se muestra vacío). Además `verificacion.html` fija "24 horas" mientras el token expira según `VERIFY_MAIL_RECUPERACION` (30 minutos en el `.env` de ejemplo).
8. **Rate limiter detrás de proxy**: `get_remote_address` usa la IP directa; tras un load balancer todas las peticiones pueden compartir cuota. `RequestMetadata` sí considera `X-Forwarded-For`, por lo que ambas lógicas son inconsistentes.
9. **`cloudinary.py` crea una instancia `app = FastAPI(...)` sin uso** e importa símbolos no utilizados (`Query`, `HTTPException`, `File`…).
10. **Guards `get_admin_user`/`get_premium_user`** siguen como placeholder.
11. **Factories duplicadas** (`get_password_service`, `get_token_service`, `get_mail_service`, `get_image_service`) en `infrastructure/` y en `container/providers.py`; solo las últimas se usan.
12. **Fugas de la regla de dependencia** (Sección 3.3): modelos de infraestructura importados desde dominio/aplicación, `AuthMailContent` y `Settings` inyectados por tipo concreto, `fastapi.status`/`UploadFile` en el dominio.
13. **Docstring de `MailProtocol` desactualizado** (menciona `generar_correo_verificacion`, que ya no forma parte del contrato).
14. **Dependencias sin uso**: `sentry-sdk` y `sqlacodegen` están en `requirements.txt` sin referencias en el código.
15. **Typo heredado `HisoryPasswordNoTable`** (falta una "t"), sin impacto funcional.
16. **Access tokens no revocables de inmediato**: al eliminar la cuenta o cambiar la contraseña se revocan sesiones (refresh), pero un access token ya emitido vive hasta su expiración natural (comportamiento esperado en JWT *stateless*).
17. **`guia de uso/env_example.txt`**: la línea final `RATE_LIMITER_ENABLED: True` usa `:` en lugar de `=`, por lo que `python-dotenv` la descarta y el limitador queda en su valor por defecto.
18. **Inconsistencias en la guía HTML**: menciona `SECRET_KEY` (la variable real es `JWT_SECRET_KEY`) y el comando `uvicorn app.main:app` (el punto de entrada real es `src.main:app`).
19. **Tests de integración** (`test/integration/`): solo hay placeholders vacíos.

### 14.4 Conclusión general
La plantilla cubre el ciclo de vida completo de una cuenta con un compromiso arquitectónico consistente: Protocolos como frontera, Casos de Uso desacoplados, Composition Root explícito, Unidad de Trabajo transaccional y, ahora, un esquema versionado con Alembic y una guía de puesta en marcha. Los pendientes de la Sección 14.3 son en su mayoría ajustes de configuración, nomenclatura y documentación; el único que conviene corregir antes de depender de esa ruta de código es `DomainError(detail=...)` (punto 5), y el de las plantillas de correo (punto 7) por su impacto visible para el usuario final.