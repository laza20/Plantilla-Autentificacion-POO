# Auth Con POO SOLID — Plantilla de Autenticación FastAPI (Clean Architecture + SOLID)

## 1. Introducción y Objetivo General

Este repositorio es una **plantilla (boilerplate) de autenticación, autorización y ciclo de vida de cuenta** construida con **FastAPI** y **PostgreSQL**, diseñada explícitamente para ser **reutilizada entre múltiples proyectos/clientes**, en lugar de ser una solución de un solo uso.

El objetivo técnico central del proyecto es demostrar cómo se puede construir un módulo de autenticación **completo** — registro, verificación por correo, login, gestión de sesiones multi-dispositivo, recuperación de contraseña, modificación de perfil, eliminación de cuenta (soft delete) y reactivación de cuenta — **sin acoplar la lógica de negocio al framework ni a proveedores externos concretos**. Esto se logra aplicando **Clean Architecture**, los principios **SOLID** y, en particular, el **Principio de Inversión de Dependencias (DIP)** implementado mediante `typing.Protocol` de Python — es decir, contratos estructurales (*duck typing* tipado) en lugar de herencia de clases abstractas (`ABC`).

En términos prácticos, esto significa que:

- Los **Casos de Uso** (`RegisterUseCase`, `LoginUseCase`, `EliminarUsuarioUseCase`, `ReactivarUsuarioUseCase`, etc.) no saben si las contraseñas se hashean con Argon2 o Bcrypt, si los correos se envían con FastAPI-Mail o SendGrid, o si las imágenes se guardan en Cloudinary o S3. Solo conocen **protocolos**.
- Cambiar de proveedor (por ejemplo, migrar de Cloudinary a AWS S3) implica crear una nueva clase que cumpla el `ImageProtocol` y modificar **una sola línea** en el contenedor de dependencias — sin tocar la capa de aplicación ni la de dominio.
- Toda operación que modifica más de una tabla (por ejemplo, cambiar una contraseña, que implica actualizar `auth_users`, insertar en `history_password` y desactivar un token de recuperación) se ejecuta dentro de una **Unidad de Trabajo** (`UnitOfWorkProtocol`) que garantiza atomicidad (commit/rollback conjunto).
- El dominio (reglas de negocio puras, como las políticas de contraseña y de mail) es, con una excepción menor señalada en la Sección 14, independiente de FastAPI.

Esta plantilla resuelve el problema recurrente de tener que reescribir el mismo flujo de autenticación end-to-end en cada nuevo proyecto backend, ofreciendo en su lugar un punto de partida arquitectónicamente sólido, testeable y extensible, que ya cubre el ciclo de vida completo de una cuenta de usuario: **alta → verificación → uso → recuperación ante pérdida de contraseña → baja (reversible) → reactivación**.

---

## 2. Características Principales y Stack Tecnológico

### Características principales

- Registro de usuarios con **carga de imagen de perfil opcional** vía `multipart/form-data`.
- **Verificación de cuenta por correo electrónico** con plantilla HTML (Jinja2) y token JWT de scope propio (`type: "verification"`), con expiración independiente de la sesión.
- **Reenvío del correo de verificación** para cuentas que quedaron pendientes de activación.
- **Login** basado en `OAuth2PasswordRequestForm` (estándar de FastAPI/OpenAPI), que además registra IP y User-Agent del dispositivo.
- **JWT de doble token**: Access Token (corta duración) + Refresh Token (larga duración), gestionados como **cookies `HttpOnly`**, no expuestos al cliente JavaScript.
- **Gestión de sesiones multi-dispositivo**: cada login persiste el hash del refresh token junto a IP/User-Agent en la tabla `sesiones`; el usuario puede listar sus sesiones activas (marcando cuál es la actual) y revocar sesiones puntuales.
- **Renovación silenciosa de sesión** (`/Refresh/Token`) sin requerir nuevo login.
- **Logout** que invalida la sesión eliminando las cookies y el registro de sesión correspondiente.
- **Recuperación de contraseña de tres pasos**: solicitud por email → verificación de token plano (hasheado en BD, nunca almacenado en texto plano) → cambio efectivo de contraseña con token de scope `reset` de corta duración transportado en una cookie con `path` restringido al endpoint de cambio.
- **Historial de contraseñas** (`history_password`): cada cambio de contraseña guarda el hash anterior antes de sobreescribirlo, dentro de la misma transacción.
- **Modificación de perfil** (email y/o imagen), con reactivación del flujo de verificación si el email cambia.
- **Eliminación de cuenta (soft delete) con confirmación por correo**: el usuario solicita la baja, recibe un enlace de confirmación, y al confirmarlo su cuenta pasa a `estado=ELIMINADO`, revocándose además **todas** sus sesiones activas.
- **Reactivación de cuenta** dentro de una ventana de tiempo configurable tras la eliminación, también confirmada por correo.
- **Hashing de contraseñas con Argon2** (vía `pwdlib`), el algoritmo recomendado actualmente por OWASP.
- **Política de contraseñas y de formato de mail** configurables como servicios de dominio.
- **Subida de imágenes a Cloudinary** con validación de tamaño y extensión antes del envío.
- **Manejo de errores centralizado**: toda excepción de dominio (`DomainError`) se traduce automáticamente a una respuesta HTTP coherente mediante un `exception_handler` global.
- **Guards de autorización** (`get_current_user`, `get_admin_user`, `get_premium_user`) listos para proteger endpoints.
- **Inyección de dependencias 100% vía FastAPI `Depends`**, sin frameworks de DI adicionales.
- **Suite de tests extensa** (unitarios con fakes/stubs propios y tests de routers con overrides de dependencias) para cada caso de uso y endpoint — ver Sección 4.1.

### Stack tecnológico (extraído de `requirements.txt`)

| Categoría | Tecnología | Rol en el proyecto |
|---|---|---|
| Framework web | `fastapi==0.136.1` | Enrutamiento HTTP, validación, inyección de dependencias |
| Servidor ASGI | `uvicorn==0.46.0` | Servidor de desarrollo/producción |
| ORM / Modelado | `sqlmodel==0.0.38` | Combina Pydantic + SQLAlchemy para modelos tipados |
| SQL Toolkit | `SQLAlchemy==2.0.49` | Motor subyacente de `sqlmodel` |
| Driver PostgreSQL | `psycopg2-binary==2.9.12` | Conexión al motor PostgreSQL |
| Migraciones | `alembic==1.18.4` | Declarado como dependencia (ver nota en Sección 10) |
| JWT | `python-jose==3.5.0` | Codificación/decodificación de tokens JWT (sesión, verificación, reset, eliminación, reactivación) |
| Tokens opacos | `secrets` (stdlib) | Generación del token plano de recuperación de contraseña, hasheado con `hashlib.sha256` antes de persistir |
| Hashing de contraseñas | `pwdlib==0.3.0` + `argon2-cffi==25.1.0` | Hash y verificación Argon2 |
| Envío de correo | `fastapi-mail==1.6.4` + `aiosmtplib==5.1.1` | Envío asíncrono de correos SMTP |
| Plantillas de correo | `Jinja2==3.1.6` | Renderizado de las 4 plantillas HTML (verificación, recuperación, eliminación, reactivación) |
| Imágenes en la nube | `cloudinary==1.44.2` | Almacenamiento y transformación de imágenes |
| Configuración | `pydantic-settings==2.14.1` | Lectura y validación tipada de variables de entorno |
| Validación de datos | `pydantic==2.13.4` | Modelos de entrada/salida (DTOs) |
| Multipart / formularios | `python-multipart==0.0.28` | Soporte para `Form()` y `UploadFile` |
| Manejo de imágenes | `pillow==12.2.0` | Dependencia transitiva para procesamiento de imágenes |
| Testing | `pytest==9.1.1`, `pytest-asyncio==1.4.0`, `pytest-cov==7.1.0` | Suite de tests unitarios e integración vía `TestClient` |
| Utilidades | `python-dotenv==1.2.2` | Carga de archivo `.env` |

**Lenguaje:** Python (tipado con `typing.Protocol`, `Optional`, uniones `str | None`, propio de Python 3.10+).

---

## 3. Arquitectura del Sistema

### 3.1 Patrón arquitectónico identificado

El proyecto implementa una variante de **Clean Architecture** (también reconocible como **Arquitectura por Capas con Inversión de Dependencias**, cercana a **Hexagonal/Ports & Adapters**). La evidencia concreta en el código:

1. **Existe una capa de Dominio pura** (`src/auth/domain/`) que define **Protocolos** (`Protocol` de `typing`) como "puertos": `AuthUserRepositoryProtocol`, `UsuarioRepositoryProtocol`, `TokenRepositoryProtocol` (sesiones), `RecuperarContraseñaProtocol`, `HistoryRepositoryProtocol`, `UnitOfWorkProtocol`, `TokenProtocol`, `PasswordProtocol`, `MailProtocol`, `ImageProtocol`, `RequestMetadataProtocol`. Estos protocolos son los **contratos** que la capa de aplicación consume, y que la infraestructura debe satisfacer.
2. **Existe una capa de Aplicación** (`src/auth/application/`) formada por **16 Casos de Uso**, organizados por sub-dominio funcional (`recover_password/`, `sesiones/`, `eliminar_usuario/`, `reactivacion_cuenta/`, más los casos de uso "planos" de registro/login/logout/refresh/verificación/modificación/reenvío), cada uno con una única responsabilidad de orquestación, recibiendo sus dependencias exclusivamente como **protocolos** por constructor.
3. **Existe una capa de Infraestructura** (`src/auth/infrastructure/`) que contiene las implementaciones concretas: `AuthUserRepository`, `UserRepository` (tabla secundaria `usuario`), `SesionRepository`, `RecoverPasswordRepository`, `HistoryPasswordRepository`, `UnitOfWork`, `TokenService` (JWT), `PasswordService` (Argon2), `MailService` (FastAPI-Mail), `ImageService` (Cloudinary). Ninguna de estas clases se referencia por su tipo concreto en la capa de Aplicación — solo se inyectan cumpliendo el protocolo correspondiente.
4. **Existe una capa de Presentación** (`src/auth/presentation/web/`) que es la única capa que "conoce" FastAPI explícitamente: `routers.py` (endpoints HTTP), `guards.py` (dependencias de autorización), `cookies/cookies.py` (gestión de cookies de sesión y de reset), `utils/request_metadata.py` (extracción de IP/User-Agent del `Request`).
5. **Existe un mecanismo explícito de Composición/Ensamblado** (`src/container/`), que actúa como el punto donde todas las capas se "cablean" entre sí (Dependency Injection Composition Root), ahora con **16 clases `Container*`** correspondientes a cada caso de uso.

### 3.2 Responsabilidad detallada de cada capa

| Capa | Carpeta | Responsabilidad | ¿Conoce FastAPI? | ¿Conoce infraestructura concreta? |
|---|---|---|---|---|
| **Dominio** | `auth/domain/` | Reglas de negocio, contratos (Protocols), excepciones de dominio | No (excepción menor, ver 3.3) | No — solo define interfaces |
| **Aplicación** | `auth/application/` | Orquesta un caso de uso completo llamando a protocolos, agrupando operaciones multi-tabla dentro de un `UnitOfWorkProtocol` | Parcialmente (usa `UploadFile` como tipo de FastAPI en firmas) | No — solo recibe protocolos por constructor |
| **Infraestructura** | `auth/infrastructure/` | Implementaciones concretas: JWT, Argon2, Cloudinary, FastAPI-Mail, SQLModel, `UnitOfWork` sobre `Session` | Sí (algunos `Depends` locales, no usados en el flujo activo — ver 6.5) | Sí — es la capa que integra proveedores reales |
| **Presentación** | `auth/presentation/web/` | Define endpoints, extrae parámetros HTTP, delega a Casos de Uso | Sí, totalmente | No directamente — recibe Casos de Uso ya construidos |
| **Composición** | `container/` | Ensambla instancias concretas para satisfacer los protocolos que exige cada Caso de Uso | Sí (usa `Depends`) | Sí — es el único lugar donde dominio e infraestructura se "encuentran" |

### 3.3 Reglas de dependencia y flujo de comunicación

La regla de dependencia de Clean Architecture se cumple **de afuera hacia adentro**:

```
Presentación  →  Aplicación  →  Dominio
Infraestructura  →  Dominio  (implementa los Protocols)
Composición (container)  →  conoce TODAS las capas (es el único punto permitido)
```

- La capa de **Dominio** no importa nada de `infrastructure/` ni de `presentation/`. Solo depende de `fastapi.UploadFile` en `protocol_image_service.py` y de `fastapi.HTTPException`/`status` en `domain/exceptions/domain.py` y `domain/exceptions/tokens.py`. Es la misma fuga de framework, menor, ya presente en versiones anteriores.
- La capa de **Aplicación** (Casos de Uso) depende exclusivamente de **Protocolos** del dominio, de modelos de datos y de servicios de dominio (`PasswordPolicyService`, `MailPolicyService`, `UserValidationService`). Nunca importa una clase concreta de `infrastructure/`.
- La capa de **Infraestructura** importa los Protocols del dominio para garantizar que sus clases cumplen el contrato esperado (el cumplimiento es estructural, no requiere herencia explícita).
- El **Contenedor de Dependencias** (`container/`) es el único módulo que importa simultáneamente Protocolos, implementaciones concretas y Casos de Uso, actuando como *Composition Root*.

---

## 4. Estructura de Carpetas y Directorios

```
.
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
│
└── src/
    ├── main.py                              # Punto de entrada: crea la app FastAPI, crea el esquema y registra el exception handler global
    │
    ├── config/
    │   └── config.py                        # Settings (pydantic-settings) — lee y valida el .env
    │
    ├── container/                           # Composition Root
    │   ├── auth_container.py                # 16 clases "Container*" — una por caso de uso
    │   └── providers.py                      # Funciones factory usadas como Depends() en los routers
    │
    ├── database/
    │   ├── client.py                        # engine de SQLModel + get_session()
    │   └── enums/
    │       └── estado_entidad.py            # EstadoEntidad: activo, eliminado, reportado, suspendido, pendiente
    │
    ├── auth/
    │   ├── domain/
    │   │   ├── protocols/
    │   │   │   ├── repository/
    │   │   │   │   ├── protocol_auth_user_repository.py   # AuthUserRepositoryProtocol
    │   │   │   │   ├── protocol_user_repository.py        # UsuarioRepositoryProtocol (tabla `usuario`)
    │   │   │   │   ├── protocol_sesion_repository.py       # TokenRepositoryProtocol (sesiones)
    │   │   │   │   ├── protocol_recover_password_repository.py  # RecuperarContraseñaProtocol
    │   │   │   │   ├── protocol_history_password_repository.py  # HistoryRepositoryProtocol
    │   │   │   │   └── protocol_unit_of_work.py            # UnitOfWorkProtocol
    │   │   │   └── service/
    │   │   │       ├── protocol_token_service.py           # TokenProtocol
    │   │   │       ├── protocol_password_service.py        # PasswordProtocol
    │   │   │       ├── protocol_mail_service.py             # MailProtocol
    │   │   │       ├── protocol_image_service.py            # ImageProtocol
    │   │   │       └── protocol_request_metadata.py         # RequestMetadataProtocol
    │   │   ├── services/
    │   │   │   ├── password_policy.py       # PasswordPolicyService
    │   │   │   ├── mail_policy.py           # MailPolicyService
    │   │   │   └── user_validation_service.py  # UserValidationService
    │   │   └── exceptions/
    │   │       ├── domain.py                # DomainError + excepciones genéricas
    │   │       ├── tokens.py                # TokenException + excepciones de token
    │   │       └── usuarios_exceptions.py   # UsuarioError + excepciones de usuario/auth
    │   │
    │   ├── application/
    │   │   ├── dtos.py                      # parse_usuario_form, parse_modificar_usuario_form
    │   │   └── use_cases/
    │   │       ├── register.py                          # RegisterUseCase
    │   │       ├── login.py                              # LoginUseCase
    │   │       ├── logout.py                             # LogoutUseCase
    │   │       ├── refresh_token.py                      # RefreshTokenUseCase
    │   │       ├── verify_email.py                       # VerifyMailUseCase
    │   │       ├── reenviar_mail.py                      # ReenviarMailUseCase
    │   │       ├── modificar_usuario.py                  # ModificarUsuarioUseCase
    │   │       ├── sesiones/
    │   │       │   ├── listar_sesiones.py                # ListarSesionesUseCase
    │   │       │   └── eliminar_sesiones.py              # EliminarSesionesUseCase
    │   │       ├── recover_password/
    │   │       │   ├── solicitud_recuperacion.py          # SolicitudRecuperacionUseCase
    │   │       │   ├── verificar_token.py                # VerificarTokenUseCase
    │   │       │   └── recuperar_contraseña.py           # RecuperarContraseñaUseCase
    │   │       ├── eliminar_usuario/
    │   │       │   ├── solicitud_eliminar_usuario.py      # SolicitudEliminacionUsuarioUseCase
    │   │       │   └── eliminar_usuario.py                # EliminarUsuarioUseCase
    │   │       └── reactivacion_cuenta/
    │   │           ├── solicitud_reactivacion_cuenta.py   # EnviarMailReactivacionUseCase
    │   │           └── reactivar_cuenta.py                # ReactivarUsuarioUseCase
    │   │
    │   ├── infrastructure/
    │   │   ├── persistence/postgres/
    │   │   │   ├── models/
    │   │   │   │   ├── models_auth_users.py       # AuthUser + DTOs asociados
    │   │   │   │   ├── models_usuario.py          # Usuario (tabla secundaria 1:1)
    │   │   │   │   ├── models_sesiones.py         # Sesiones, SesionesVisual, ListaSesiones
    │   │   │   │   ├── models_recover_password.py # RecoverPassword
    │   │   │   │   └── models_history_password.py # HistoryPassword
    │   │   │   ├── repository/
    │   │   │   │   ├── auth_user_repository.py     # AuthUserRepository
    │   │   │   │   ├── usuario_repository.py       # UserRepository (tabla `usuario`)
    │   │   │   │   ├── sesion_repository.py        # SesionRepository
    │   │   │   │   ├── recover_password_repository.py    # RecoverPasswordRepository
    │   │   │   │   ├── history_password_repository.py    # HistoryPasswordRepository
    │   │   │   │   └── unit_of_work.py             # UnitOfWork
    │   │   │   └── schemas/
    │   │   │       └── schemas_recepcion.py        # SolicitudRecuperacionRequest, SolicitudReactivacionRequest, ModificarPassword
    │   │   ├── security/
    │   │   │   ├── security.py                     # PasswordService (Argon2)
    │   │   │   └── tokens/tokens.py                # TokenService (JWT + tokens opacos)
    │   │   ├── mail/mail.py                        # MailService (FastAPI-Mail + Jinja2)
    │   │   ├── images/
    │   │   │   ├── cloudinary_config.py
    │   │   │   └── cloudinary.py                   # ImageService
    │   │   └── templates/
    │   │       ├── verificacion.html
    │   │       ├── recuperacion_contraseña.html
    │   │       ├── eliminar_cuenta.html
    │   │       └── reactivar_cuenta.html
    │   │
    │   └── presentation/web/
    │       ├── routers.py                   # Endpoints públicos del módulo de usuarios (17 endpoints)
    │       ├── guards.py                    # AuthDependencies
    │       ├── cookies/cookies.py           # CookiesService
    │       └── utils/request_metadata.py    # RequestMetadata
    │
    └── test/                                # Suite de tests (ver 4.1)
```

### 4.1 Nota sobre la carpeta `test/`

El proyecto incluye una **suite de tests propia y bastante madura**, separada en:

- `test/unit/auth/domain/fakes/` — implementaciones **en memoria** de cada protocolo de repositorio (`FakeUserRepository`, `FakeSesionRepository`, `FakeRecuperarContraseñaRepository`, `FakeHistoryPasswordRepository`, `FakeUsuarioRepository`), usadas en lugar de mocks para tests de Casos de Uso.
- `test/unit/auth/domain/service/` — **stubs** de cada protocolo de servicio (`StubTokenService`, `StubPasswordService`, `StubMailService`, `StubImageService`, `StubPasswordPolicy`, `StubMailPolicy`, `StubUnitOfWork`, `StubCookiesService`).
- `test/unit/auth/domain/use_case/` — un archivo de test por Caso de Uso, ejercitando camino feliz y cada excepción de dominio esperada.
- `test/fixtures/` — clases `*TestEnvironment` que arman el grafo de dependencias fake/stub para cada Caso de Uso, evitando repetir el cableado en cada test.
- `test/presentation/web/` — tests de los routers usando `TestClient` de FastAPI, con `app.dependency_overrides` para reemplazar cada Caso de Uso por un **stub configurable** (`crear_override`).
- `test/integration/` — carpeta reservada para tests de integración contra la base de datos real (actualmente con archivos placeholder sin contenido).

Como los fakes/stubs implementan los mismos Protocols que la infraestructura real, el patrón es directamente el DIP aplicado a testing: **ningún test necesita levantar PostgreSQL, Cloudinary o un servidor SMTP real** para validar la lógica de negocio.

---

## 5. Ciclo de Vida de una Petición (Flujo de Ejecución)

### 5.1 Explicación paso a paso (caso: Login)

1. El cliente envía `POST /{NOMBRE_APP}/usuarios/login` con `username` (email) y `password` en formato `application/x-www-form-urlencoded` (estándar `OAuth2PasswordRequestForm`).
2. FastAPI enruta la petición a `routers.py :: logearse()`.
3. FastAPI resuelve la dependencia `Depends(get_login_use_case)` **antes** de ejecutar la función del endpoint, disparando la cadena de resolución de `providers.py`: `get_settings()`, `get_auth_user_repository()` (→ `AuthUserRepository(session)`), `get_token_service()` (→ `TokenService`, tipado `TokenProtocol`), `get_password_service()` (→ `PasswordService`, tipado `PasswordProtocol`), `get_sesion_repository()` (→ `SesionRepository`, tipado `TokenRepositoryProtocol`), `get_unit_of_work()` (→ `UnitOfWork(session)`), `get_user_validation_service()`.
4. `get_login_use_case()` pasa todo eso a `ContainerLogin(...)`, cuya propiedad `.login_use_case` construye la instancia final de `LoginUseCase`.
5. FastAPI inyecta ese `LoginUseCase` ya ensamblado en el endpoint, junto con `RequestMetadata(request)` para extraer IP y User-Agent.
6. El endpoint llama a `login_use_case.ejecutar(usuario.username, usuario.password, ip, user_agent)`.
7. Dentro del Caso de Uso (capa de Aplicación):
   a. `UserValidationService.obtener_usuario_existente(mail)` busca al usuario vía `AuthUserRepositoryProtocol.obtener_por_email()` (que **solo** devuelve usuarios `ACTIVO`) y lanza `UsuarioNoEncontrado` si no existe.
   b. `PasswordProtocol.verify_password(...)` valida la contraseña (Argon2). Si falla, se lanza `LoginError`.
   c. `TokenProtocol.create_user_tokens(user_id)` genera el par access/refresh token (JWT).
   d. `TokenProtocol.hash_token(refresh_token)` calcula el hash SHA-256 del refresh token.
   e. Dentro de un `UnitOfWorkProtocol`, `TokenRepositoryProtocol.insertar_sesion(hash, id_usuario, ip, user_agent)` persiste el registro de la sesión.
8. El Caso de Uso retorna un `LoginResponse` (tokens + datos públicos del usuario); el router adjunta ambos tokens como cookies `HttpOnly` vía `CookiesService.set_auth_cookies`.
9. Si en cualquier punto se lanzó una excepción que hereda de `DomainError`, es interceptada por el **exception handler global** registrado en `main.py`, que traduce `exc.status_code` y `exc.message` a una respuesta JSON estándar — ningún router necesita capturarla manualmente.

### 5.2 Diagrama textual del recorrido de datos

```
Cliente HTTP
    │  POST /{NOMBRE_APP}/usuarios/login
    ▼
presentation/web/routers.py :: logearse()          ← Capa de Presentación
    │  Depends(get_login_use_case) + RequestMetadata(request)
    ▼
container/providers.py :: get_login_use_case
    ├─ get_auth_user_repository()  → AuthUserRepository
    ├─ get_token_service()          → TokenService     (TokenProtocol)
    ├─ get_password_service()       → PasswordService  (PasswordProtocol)
    ├─ get_sesion_repository()      → SesionRepository (TokenRepositoryProtocol)
    ├─ get_unit_of_work()           → UnitOfWork       (UnitOfWorkProtocol)
    └─ get_user_validation_service()
    │  construye
    ▼
container/auth_container.py :: ContainerLogin.login_use_case → LoginUseCase(...)
    ▼
application/use_cases/login.py :: LoginUseCase        ← Capa de Aplicación
    1. UserValidationService.obtener_usuario_existente(...)
    2. PasswordProtocol.verify_password(...)
    3. TokenProtocol.create_user_tokens(...) + hash_token(...)
    4. with UnitOfWorkProtocol: TokenRepositoryProtocol.insertar_sesion(...)
    │
    ├─ implementado por → infrastructure/security/security.py :: PasswordService (Argon2)
    ├─ implementado por → infrastructure/security/tokens/tokens.py :: TokenService (JWT)
    └─ implementado por → infrastructure/persistence/postgres/repository/sesion_repository.py :: SesionRepository
    ▼
PostgreSQL
    ▼
Respuesta JSON (LoginResponse) + Set-Cookie: access_token / refresh_token (HttpOnly)
```

Si en cualquier capa se lanza un `DomainError`:

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

| Protocolo | Métodos exigidos (resumen) | Implementación concreta actual |
|---|---|---|
| `AuthUserRepositoryProtocol` | `insertar`, `obtener_por_id_sin_activar`, `activar`, `obtener_por_email`, `obtener_por_id`, `modificar_contraseña`, `obtener_por_email_sin_activar`, `modificar_usuario`, `eliminar_usuario`, `obtener_usuario_eliminado_por_mail`, `obtener_usuario_eliminado_por_id`, `activar_usuario_eliminado` | `AuthUserRepository` (SQLModel/PostgreSQL) |
| `UsuarioRepositoryProtocol` | `insertar` | `UserRepository` (tabla secundaria `usuario`) |
| `TokenRepositoryProtocol` | `insertar_sesion`, `listar_sesiones`, `eliminar_sesion`, `eliminar_por_hash`, `eliminar_todas_las_sesiones_de_un_usuario` | `SesionRepository` |
| `RecuperarContraseñaProtocol` | `insertar_recuperacion_contraseña`, `verificar_token`, `invalidar_tokens_anteriores`, `desactivar_token_utilizado` | `RecoverPasswordRepository` |
| `HistoryRepositoryProtocol` | `insertar_history_repository` | `HistoryPasswordRepository` |
| `UnitOfWorkProtocol` | `__enter__`, `__exit__` (commit al salir sin excepción, rollback si se propaga una) | `UnitOfWork` |
| `TokenProtocol` | `create_user_tokens`, `create_access_token`, `create_refresh_token`, `get_user_id_from_access_token`, `get_user_id_from_refresh_token`, `hash_token`, `generar_token_plano`, `create_reset_token`, `get_current_reset_scope`, `create_verificacion_token`, `get_user_id_from_verificacion_token`, `create_eliminacion_token`, `get_user_id_from_eliminacion_token`, `create_reactivacion_token`, `get_user_id_from_reactivacion_token` | `TokenService` (JWT vía `python-jose` + tokens opacos vía `secrets`) |
| `PasswordProtocol` | `hash_password`, `verify_password` | `PasswordService` (Argon2 vía `pwdlib`) |
| `MailProtocol` | `enviar_mail` (async), `generar_correo_verificacion`, `generar_correo_recuperacion`, `generar_correo_eliminacion`, `generar_correo_reactivacion` | `MailService` (FastAPI-Mail + Jinja2) |
| `ImageProtocol` | `insertar_imagen` | `ImageService` (Cloudinary) |
| `RequestMetadataProtocol` | `get_ip`, `get_user_agent` | `RequestMetadata` |

Cada protocolo de repositorio y de servicio de "primera generación" (`AuthUserRepositoryProtocol`, `TokenRepositoryProtocol`, `UnitOfWorkProtocol`, `UsuarioRepositoryProtocol`, `RequestMetadataProtocol`) incorpora ahora **docstrings a nivel de método** explicando el propósito de negocio de cada operación, en el mismo espíritu que los docstrings extensísimos ya presentes en `ImageProtocol`, `PasswordProtocol` y `MailProtocol` desde la primera versión de la plantilla.

`TokenProtocol` es, por lejos, el protocolo más grande: refleja que el sistema emite **cinco tipos distintos de JWT** distinguidos por el claim `"type"` (`access`, `refresh`, `verification`, `reset`, `eliminacion`, `reactivacion`), cada uno con su propio método de creación/decodificación y su propia excepción de "token inactivo" si el payload no trae `sub` (ver 6.4).

### 6.2 Dominio — Servicios (`domain/services/`)

- **`PasswordPolicyService.validar(contraseña)`**: ≥ 8 caracteres, mayúscula, minúscula, dígito y carácter especial. Lanza `ContraseñaNoSegura` (400).
- **`MailPolicyService.validar(mail)`**: exige un único `@`, un punto después del `@` con al menos un carácter de separación, y una longitud mínima de 6 caracteres. Lanza `MailNoValido` (400). Es utilizado por `RegisterUseCase`, `ModificarUsuarioUseCase`, `ReenviarMailUseCase` y `EnviarMailReactivacionUseCase` — cualquier flujo que reciba un email "en crudo" desde el cliente pasa por esta validación antes de tocar la base de datos.
- **`UserValidationService`**: envuelve al `AuthUserRepositoryProtocol` para centralizar la regla "si el usuario no existe, lanzar `UsuarioNoEncontrado`". Expone `obtener_usuario_existente(email)` (Login) y `get_user(current_user)` (perfil del usuario autenticado).

Ambos servicios de política son **puros** (sin dependencias externas, solo expresiones regulares), lo que los hace triviales de testear de forma aislada — de hecho cuentan con sus propios archivos de test (`test_password_policy.py`, `test_mail_policy.py`).

### 6.3 Aplicación — Casos de Uso (`application/use_cases/`)

#### Ciclo de alta de cuenta

- **`RegisterUseCase.ejecutar(usuario, imagen)`**: normaliza el DTO a `AuthUser`, valida política de mail y de contraseña, hashea la contraseña, sube la imagen si se adjuntó, inserta el usuario **y** su registro correspondiente en la tabla secundaria `usuario` dentro de la misma unidad de trabajo, genera un token de verificación (`create_verificacion_token`, `type: "verification"`, expira según `VERIFY_MAIL_RECUPERACION`) y envía el correo de bienvenida.
- **`VerifyMailUseCase.ejecutar(token)`**: decodifica el token de verificación, busca al usuario **sin filtrar por estado** (`obtener_por_id_sin_activar`), lo activa (`estado=ACTIVO`, `is_verified=True`) dentro de una unidad de trabajo y emite inmediatamente un par de tokens de sesión — el usuario queda logueado al verificar su correo.
- **`ReenviarMailUseCase.ejecutar(mail_usuario)`**: para cuentas que quedaron `PENDIENTE`, reenvía el correo de verificación con un nuevo token, tras validar el formato del mail.

#### Sesión y perfil

- **`LoginUseCase.ejecutar(email, password, ip, user_agent)`**: ver flujo detallado en la Sección 5.1.
- **`LogoutUseCase.ejecutar(refresh_token)`**: hashea el refresh token recibido y, dentro de una unidad de trabajo, lo elimina de la tabla `sesiones` vía `eliminar_por_hash`.
- **`RefreshTokenUseCase.ejecutar(refresh_token)`**: valida el refresh token y emite un nuevo access token (no reemite refresh token — *sliding session* parcial).
- **`ModificarUsuarioUseCase.ejecutar(id_usuario, usuario, imagen)`**: permite actualizar email y/o imagen. Si cambia el email, revalida la política de mail, pasa el `estado` a `PENDIENTE` de nuevo y dispara un nuevo correo de verificación tras persistir el cambio. Soporta invocarse solo con imagen (sin datos de `UserModifyDTO`), reutilizando una copia del usuario existente como base de normalización.

#### Sesiones multi-dispositivo

- **`ListarSesionesUseCase.ejecutar(id_usuario, ip)`**: lista todas las sesiones del usuario y marca con `es_actual=True` aquella cuya IP coincide con la de la petición en curso.
- **`EliminarSesionesUseCase.ejecutar(id_sesion, id_usuario)`**: revoca una sesión puntual (filtrando también por `id_usuario`, para que un usuario no pueda revocar sesiones ajenas), dentro de una unidad de trabajo.

#### Recuperación de contraseña (flujo de 3 pasos)

- **`SolicitudRecuperacionUseCase.ejecutar(email)`**: genera un token **plano** (`generar_token_plano`, criptográficamente aleatorio, no JWT), invalida cualquier token de recuperación previo del usuario (`invalidar_tokens_anteriores`), persiste el **hash** del token nuevo con su expiración (`VERIFY_MAIL_RECUPERACION` minutos) y envía por correo la URL con el token en texto plano — el valor en claro nunca se guarda en base de datos.
- **`VerificarTokenUseCase.ejecutar(token)`**: hashea el token recibido, lo busca y valida vigencia vía `RecuperarContraseñaProtocol.verificar_token`, y si es válido emite un **JWT de scope `reset`** (`create_reset_token`, expira según `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES`) que el router coloca en una cookie `reset_token` con `path` restringido al endpoint de cambio de contraseña.
- **`RecuperarContraseñaUseCase.ejecutar(id_usuario, nueva_contraseña)`**: valida la política de contraseña, la hashea, y dentro de una **única unidad de trabajo**: (1) inserta el hash anterior en `history_password`, (2) actualiza la contraseña del usuario, (3) desactiva el token de recuperación utilizado. Si cualquiera de los tres pasos falla, se lanza la excepción correspondiente (`ErrorCreacion`, `UsuarioNoModificado` o `TokenNoDesactivado`) y la transacción completa se revierte.

#### Baja y reactivación de cuenta

- **`SolicitudEliminacionUsuarioUseCase.ejecutar(id_usuario)`**: genera un token de scope `eliminacion` (`create_eliminacion_token`, expira según `ELIMINACION_CUENTA`) y envía el correo de confirmación de baja.
- **`EliminarUsuarioUseCase.ejecutar(token_hash)`**: decodifica el token de eliminación, y dentro de una unidad de trabajo marca al usuario como `estado=ELIMINADO` (con `eliminado_en=date.today()`) **y** revoca todas sus sesiones activas (`TokenRepositoryProtocol.eliminar_todas_las_sesiones_de_un_usuario`). Es un *soft delete*: el registro nunca se borra físicamente.
- **`EnviarMailReactivacionUseCase.ejecutar(mail_usuario)`**: busca al usuario **eliminado** por mail, genera un token de scope `reactivacion` (`create_reactivacion_token`) y envía el correo correspondiente.
- **`ReactivarUsuarioUseCase.ejecutar(token)`**: decodifica el token de reactivación, valida que el usuario exista y esté efectivamente `ELIMINADO` (si no, `UsuarioNoEliminado`), valida que no haya expirado la ventana de gracia comparando `eliminado_en + REACTIVACION_CUENTA días` contra la fecha actual (si venció, `PeriodoReactivacionFinalizado`), y de ser todo válido reactiva la cuenta (`estado=ACTIVO`, `eliminado_en=None`) dentro de una unidad de trabajo.

### 6.4 Dominio — Excepciones (`domain/exceptions/`)

`DomainError` sigue siendo la clase base de **toda** excepción de negocio, con `message` y `status_code` fijado por subclase:

```python
class DomainError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code or getattr(self, "status_code", 400)
        super().__init__(self.message)
```

Jerarquías actuales:

- **`domain.py`**: `ContraseñaNoSegura` (400), `MailNoValido` (400), `SinCargas` (409), `LongitudExcedida` (422), `LimiteTamañoSuperado` (413), `ExtensionNoPermitida` (400), `ErrorCloudinary` (500), `MailRepetido` (409), `ErrorCreacion` (409), `ErrorEliminacion` (409).
- **`tokens.py`**: `TokenException` → `TokenExpirado` (403), `VerificacionExpirada` (403), `TokenNoDesactivado` (409), `TokenNoVerificado` (409), `TokenInvalido` (401), `TokenResetInactivo` (401), `TokenVerificacionInactivo` (401), `TokenReactivacionInactivo` (401), `TokenEliminacionInactivo` (401), `VerificacionInvalida` (401).
- **`usuarios_exceptions.py`**: `UsuarioError` (400) → `LoginError` (400), `UsuarioNoModificado` (409), `UsuarioNoEliminado` (409), `PeriodoReactivacionFinalizado` (409), `UsuarioNoEncontrado` (409), `UsuarioActivo` (400), `NoAutenticado` (401), `SinAccessToken` (401), `SinRefreshToken` (401), `UsuariosNoEncontrados` (409), `AvatarError` (409), `TiempoInterrupcionInicioSesion` (403), `UsuarioInactivo` (423); y `ResultadoInvalido` (409) como subclase directa de `DomainError`.

> **Corrección respecto a versiones anteriores**: en una iteración previa existían **dos clases distintas llamadas `TokenInvalido`** (una en `domain/exceptions/tokens.py` y otra en `domain/exceptions/usuarios_exceptions.py`), lo que provocaba que un `except TokenInvalido` en un Caso de Uso no capturara la excepción realmente lanzada por `TokenService`. Esa colisión **ya fue resuelta**: `usuarios_exceptions.py` no vuelve a declarar `TokenInvalido`, y toda la infraestructura de tokens (`TokenService`) importa una única versión desde `domain/exceptions/tokens.py`.

Gracias a este diseño, el manejo de errores sigue completamente centralizado: **ningún router necesita un bloque `try/except` genérico** (el único router que captura explícitamente excepciones — `verificar_mail`, para `VerificacionExpirada`/`VerificacionInvalida` — lo hace de forma redundante con el handler global, ya que ambas heredan de `DomainError`).

### 6.5 Infraestructura

| Archivo | Clase / Función | Rol |
|---|---|---|
| `persistence/postgres/models/models_auth_users.py` | `AuthUser` (tabla), `AuthUserNoTable`, `UsuarioCreado`, `UserRegisterDTO`, `UserModifyDTO`, `AuthUserEmailValidation`, `UserTokens`, `UsuarioLogeado`, `LoginResponse`, `AuthUserNoImage` | Modelo de tabla + DTOs de entrada/salida |
| `persistence/postgres/models/models_usuario.py` | `Usuario` | Tabla secundaria de datos de negocio, relación 1:1 con `auth_users` reutilizando `id_usuario` como PK/FK |
| `persistence/postgres/models/models_sesiones.py` | `Sesiones` (tabla), `SesionesNoTable`, `SesionesVisual`, `ListaSesiones` | Sesiones multi-dispositivo; `SesionesVisual` es la proyección pública (sin el hash del token) con el flag `es_actual` |
| `persistence/postgres/models/models_recover_password.py` | `RecoverPassword` (tabla), `RecoverPasswordNoTable` | Tokens de recuperación de contraseña (hash + expiración + `usado`) |
| `persistence/postgres/models/models_history_password.py` | `HistoryPassword` (tabla), `HisoryPasswordNoTable` | Historial de hashes de contraseña anteriores |
| `persistence/postgres/repository/auth_user_repository.py` | `AuthUserRepository` | Implementa `AuthUserRepositoryProtocol` sobre `Session` |
| `persistence/postgres/repository/usuario_repository.py` | `UserRepository` | Implementa `UsuarioRepositoryProtocol` (tabla `usuario`) |
| `persistence/postgres/repository/sesion_repository.py` | `SesionRepository` | Implementa `TokenRepositoryProtocol` |
| `persistence/postgres/repository/recover_password_repository.py` | `RecoverPasswordRepository` | Implementa `RecuperarContraseñaProtocol` |
| `persistence/postgres/repository/history_password_repository.py` | `HistoryPasswordRepository` | Implementa `HistoryRepositoryProtocol` |
| `persistence/postgres/repository/unit_of_work.py` | `UnitOfWork` | Implementa `UnitOfWorkProtocol`: `commit()` al salir del `with` sin excepción, `rollback()` si se propaga una |
| `security/security.py` | `PasswordService`, `get_password_service` | Hash/verificación Argon2 |
| `security/tokens/tokens.py` | `TokenService`, `get_token_service` | Codificación/decodificación de los 6 tipos de JWT + generación/hash del token opaco de recuperación |
| `mail/mail.py` | `MailService`, `get_mail_service` | Renderizado Jinja2 (4 plantillas) + envío async vía `FastMail` |
| `images/cloudinary_config.py` | — | Configuración global del SDK `cloudinary` |
| `images/cloudinary.py` | `ImageService`, `get_image_service` | Validación (tamaño ≤ 5 MB, extensiones `jpg/jpeg/png/webp`) + subida a Cloudinary |
| `templates/*.html` | — | Plantillas de verificación, recuperación, eliminación y reactivación (mismo sistema de diseño, tema oscuro, CSS embebido) |

> **Observación de diseño (duplicación de factories)**: al igual que en versiones anteriores, `security.py`, `tokens.py`, `mail.py` y `cloudinary.py` definen **cada uno su propia función `get_*_service`** a nivel de módulo de infraestructura, que no son las efectivamente utilizadas por los routers (el sistema de DI real pasa por `container/providers.py`). Siguen siendo código muerto o una capa de conveniencia no documentada — ver Sección 14.

### 6.6 Presentación (`presentation/web/`)

- **`cookies/cookies.py` — `CookiesService`**: `get_cookie_settings()` decide `secure`/`samesite` según `settings.is_prod`. Expone `set_auth_cookies` (access 15 min + refresh 7 días, hardcodeados — ver Sección 14), `set_access_cookie`, `delete_auth_cookies` y **`set_reset_cookie`** (nueva): fija la cookie `reset_token` con `max_age` derivado de `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES` y, a diferencia de las demás cookies, con un **`path` explícito** (el del endpoint `PATCH /modificar/password`), de forma que el navegador no la envíe en ninguna otra ruta de la API.
- **`utils/request_metadata.py` — `RequestMetadata`**: implementa `RequestMetadataProtocol`. `get_ip()` prioriza el header `X-Forwarded-For` (para despliegues detrás de proxy/load balancer) y cae a `request.client.host` si no está presente. `get_user_agent()` devuelve el header `user-agent` o `"Desconocido"`.
- **`guards.py` — `AuthDependencies`**: expone `get_current_user` (decodifica el JWT de la cookie `access_token`, valida `type == "access"`, busca el usuario activo por ID), `get_admin_user` y `get_premium_user`. Estos dos últimos ahora lanzan explícitamente `NotImplementedError` con un mensaje que documenta la razón (falta el campo `role` en `AuthUser`) — un cambio deliberado respecto a dejarlos simplemente sin usar, para que cualquier intento de invocarlos falle de forma clara y explicable en vez de con un `AttributeError` genérico.
- **`routers.py`**: capa HTTP delgada con **17 endpoints** (ver Sección 9 para el detalle completo por subsistema). El prefijo del router (`/{settings.NOMBRE_APP}/usuarios`) sigue construyéndose a partir del **singleton `settings`** importado directamente de `config.py`, por la misma razón que en versiones anteriores (el prefijo de un `APIRouter` se fija en tiempo de importación).

---

## 7. Configuración y Variables de Entorno

Toda la configuración se centraliza en `src/config/config.py` mediante `pydantic_settings.BaseSettings`, que carga automáticamente un archivo `.env` y **valida los tipos al arrancar la aplicación** (fail-fast).

| Variable | Tipo | Obligatoria | Módulo consumidor | Propósito |
|---|---|---|---|---|
| `is_prod` | `bool` (default `False`) | No | `CookiesService` | Determina `secure`/`samesite` de las cookies |
| `DATABASE_URL` | `str` | Sí | `database/client.py` | Cadena de conexión a PostgreSQL |
| `JWT_SECRET_KEY` | `str` | Sí | `TokenService` | Clave secreta de firma de todos los JWT |
| `ALGORITHM` | `str` | Sí | `TokenService` | Algoritmo de firma JWT (ej. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | Sí | `TokenService` | Duración del access token (JWT) en minutos |
| `REFRESH_TOKEN_DURATION` | `int` | Sí | `TokenService` | Duración del refresh token (JWT) en días |
| `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES` | `int` | Sí | `TokenService`, `CookiesService` | Duración del JWT de scope `reset` (y de la cookie `reset_token`) tras verificar el token de recuperación |
| `VERIFY_MAIL_RECUPERACION` | `int` | Sí | `TokenService` | Duración en minutos del token de verificación de mail **y** del token de recuperación de contraseña (nombre compartido entre ambos flujos — ver Sección 14) |
| `EXPIRACION_MAIL_RECUPERACION` | `int` | Sí | `Settings` (declarada, no consumida) | Reservada; actualmente no referenciada por ningún Caso de Uso o servicio (ver Sección 14) |
| `ELIMINACION_CUENTA` | `int` | Sí | `TokenService` | Duración en minutos del token de confirmación de eliminación de cuenta |
| `REACTIVACION_CUENTA` | `int` | Sí | `TokenService`, `ReactivarUsuarioUseCase` | Duración del JWT de reactivación (en **minutos**) y, en `ReactivarUsuarioUseCase`, ventana de gracia post-eliminación (en **días**) — mismo valor de configuración interpretado con dos unidades distintas (ver Sección 14) |
| `MAIL_USERNAME` / `MAIL_PASSWORD` / `MAIL_FROM` / `MAIL_PORT` / `MAIL_SERVER` | `str`/`int` | Sí | `MailService` | Credenciales y host SMTP |
| `MAIL_STARTTLS` (default `True`) / `MAIL_SSL_TLS` (default `False`) / `USE_CREDENTIALS` (default `True`) | `bool` | No | `MailService` | Configuración de la conexión SMTP |
| `NOMBRE_APP` | `str` | Sí | `routers.py`, `MailService`, varios Casos de Uso | Nombre lógico de la app; prefijo de rutas, carpeta de Cloudinary y branding del correo |
| `BASE_URL` | `str` | Sí | Casos de uso que generan URLs de correo | URL base pública para construir los enlaces de verificación/recuperación/eliminación/reactivación |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` / `CLOUDINARY_UPLOAD_PRESET` | `str` | Sí | `cloudinary_config.py`, `ImageService` | Credenciales y preset de Cloudinary |

`model_config` usa `extra="ignore"`, por lo que variables adicionales en el `.env` no declaradas se ignoran silenciosamente.

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
cat <<'EOF' > .env
is_prod=False
DATABASE_URL=postgresql://usuario:tu_clave_secreta@localhost:5432/auth_db
JWT_SECRET_KEY=tu_clave_secreta_larga_y_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_DURATION=7
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=15
VERIFY_MAIL_RECUPERACION=30
EXPIRACION_MAIL_RECUPERACION=30
ELIMINACION_CUENTA=60
REACTIVACION_CUENTA=30
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
#    createdb auth_db

# 7. Levantar el servidor de desarrollo
uvicorn src.main:app --reload

# 8. (Opcional) Ejecutar la suite de tests
pytest
```

Tras el arranque:
- Documentación interactiva: `http://localhost:8000/docs` (Swagger) y `http://localhost:8000/redoc`.
- Las tablas se crean automáticamente al iniciar la app mediante `SQLModel.metadata.create_all(engine)` en `main.py` — no requiere migraciones para el arranque inicial (ver nota sobre Alembic en la Sección 10).

---

## 9. Subsistema de Autenticación, Autorización y Seguridad

### 9.1 Registro

`POST /{NOMBRE_APP}/usuarios/registrar` (`multipart/form-data`: `email`, `password`, `imagen` opcional). Flujo: valida política de mail y de contraseña → hashea con Argon2 → sube imagen si corresponde → inserta en `auth_users` y en `usuario` (misma transacción) → genera un **token de verificación de scope propio** (`create_verificacion_token`, `type: "verification"`, expira según `VERIFY_MAIL_RECUPERACION` — ya no reutiliza el access token de sesión) → envía el correo de bienvenida.

### 9.2 Verificación de email

`GET /{NOMBRE_APP}/usuarios/verificar/{token}` activa la cuenta (`estado=ACTIVO`, `is_verified=True`) y emite inmediatamente un par access/refresh, dejando al usuario logueado sin login manual adicional.

`POST /{NOMBRE_APP}/usuarios/reenviar/mail` permite reenviar este correo si el token original expiró o se perdió, siempre que la cuenta siga `PENDIENTE`.

### 9.3 Login y sesiones multi-dispositivo

`POST /{NOMBRE_APP}/usuarios/login` usa `OAuth2PasswordRequestForm`. Solo autentica usuarios `ACTIVO`. Cada login exitoso persiste una fila en `sesiones` con el hash del refresh token, la IP y el User-Agent del cliente.

- `GET /{NOMBRE_APP}/usuarios/listar_sesiones` — devuelve todas las sesiones del usuario autenticado, marcando `es_actual=True` en la que coincide con la IP de la petición.
- `DELETE /{NOMBRE_APP}/usuarios/eliminar_sesion/{id_sesion}` — revoca una sesión puntual (por ejemplo, para cerrar sesión remotamente en otro dispositivo).

### 9.4 Ciclo de vida de los tokens JWT

| Token | Claim `type` | Duración | Transporte |
|---|---|---|---|
| Access | `"access"` | `ACCESS_TOKEN_EXPIRE_MINUTES` | Cookie `access_token` (`HttpOnly`) |
| Refresh | `"refresh"` | `REFRESH_TOKEN_DURATION` días | Cookie `refresh_token` (`HttpOnly`) |
| Verificación de mail | `"verification"` | `VERIFY_MAIL_RECUPERACION` minutos | Enlace por correo |
| Reset de contraseña | `"reset"` | `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES` minutos | Cookie `reset_token` (`HttpOnly`, `path` restringido) |
| Eliminación de cuenta | `"eliminacion"` | `ELIMINACION_CUENTA` minutos | Enlace por correo |
| Reactivación de cuenta | `"reactivacion"` | `REACTIVACION_CUENTA` minutos | Enlace por correo |

Todos se firman con `JWT_SECRET_KEY`/`ALGORITHM` vía `python-jose`. `get_user_id_from_access_token` valida además el claim `type == "access"`, evitando que un refresh token (u otro scope) sea usado como credencial de sesión. El token de recuperación de contraseña (paso 1 del flujo, Sección 9.5) **no** es JWT: es un valor opaco (`secrets.token_urlsafe(32)`) del que solo se persiste el hash SHA-256, siguiendo la misma lógica que un refresh token de sesión.

### 9.5 Recuperación de contraseña (flujo de 3 pasos)

1. `POST /{NOMBRE_APP}/usuarios/solicitud/recuperacion` — el usuario pide recuperar su contraseña con su email. Se genera un token opaco, se invalidan tokens anteriores del usuario, se persiste el hash con expiración y se envía el enlace por correo.
2. `GET /{NOMBRE_APP}/usuarios/recuperar/password/{token}` — el usuario hace clic en el enlace. El backend verifica el hash y la vigencia, y si es válido emite un JWT de scope `reset` en la cookie `reset_token` (con `path` restringido a `PATCH /modificar/password`, de forma que esa cookie no viaje a ningún otro endpoint).
3. `PATCH /{NOMBRE_APP}/usuarios/modificar/password` — con la cookie `reset_token` presente, el usuario envía la nueva contraseña. El backend decodifica el `reset_token` para obtener el `id_usuario`, valida la política de contraseña, y en una única transacción: guarda el hash anterior en el historial, actualiza la contraseña y desactiva el token de recuperación usado.

### 9.6 Modificación de perfil

`PUT /{NOMBRE_APP}/usuarios/modificar/usuario` (`multipart/form-data`, autenticado) permite actualizar `email` y/o `imagen`. Si el email cambia, la cuenta vuelve a `estado=PENDIENTE` y se dispara un nuevo correo de verificación — el usuario deberá reverificar su nuevo email antes de poder volver a iniciar sesión con él.

### 9.7 Eliminación de cuenta (soft delete)

1. `DELETE /{NOMBRE_APP}/usuarios/eliminar/usuario` (autenticado) — solicita la baja; se envía un correo de confirmación con un token de scope `eliminacion`.
2. `GET /{NOMBRE_APP}/usuarios/eliminar/cuenta/{token}` — al confirmar, la cuenta pasa a `estado=ELIMINADO` con `eliminado_en=hoy`, **se revocan todas las sesiones activas del usuario** y se borran las cookies de sesión de la respuesta. El registro nunca se elimina físicamente de la base de datos.

### 9.8 Reactivación de cuenta

1. `GET /{NOMBRE_APP}/usuarios/solicitud/reactivacion/cuenta` — el usuario solicita reactivar una cuenta eliminada indicando su email; se envía un correo con un token de scope `reactivacion`. (Nota de diseño: este endpoint está declarado como `GET` pero recibe el email en el cuerpo de la petición — ver Sección 14).
2. `GET /{NOMBRE_APP}/usuarios/reactivar/cuenta/{token}` — si el usuario existe, está efectivamente `ELIMINADO` y no se venció la ventana de `REACTIVACION_CUENTA` días desde la baja, la cuenta vuelve a `estado=ACTIVO` y se limpia `eliminado_en`.

### 9.9 Cookies de sesión

`CookiesService` fija `httponly=True` siempre y ajusta `secure`/`samesite` según `is_prod`. Los `max_age` de `access_token`/`refresh_token` siguen **hardcodeados** (`15 * 60` y `7 * 24 * 60 * 60` segundos) en vez de derivarse de `ACCESS_TOKEN_EXPIRE_MINUTES`/`REFRESH_TOKEN_DURATION` — ver Sección 14. La cookie `reset_token`, en cambio, sí deriva su `max_age` de `RESET_PASSWORD_TOKEN_EXPIRE_MINUTES`.

### 9.10 Renovación y cierre de sesión

`POST /{NOMBRE_APP}/usuarios/Refresh/Token` lee la cookie `refresh_token`, la valida y emite un nuevo access token sin reemitir refresh token. `POST /{NOMBRE_APP}/usuarios/Logout` elimina el registro de sesión correspondiente al refresh token (vía su hash) y borra ambas cookies — a diferencia de un simple borrado de cookies, esto sí invalida la sesión también del lado del servidor, por lo que un refresh token robado **no** puede seguir usándose tras el logout (aunque el access token de corta duración, si ya fue emitido, sigue siendo válido hasta su propia expiración natural, al ser JWT *stateless*).

### 9.11 Autorización basada en Guards

`get_current_user` está cableado en todos los endpoints autenticados. `get_admin_user`/`get_premium_user` siguen siendo un placeholder explícito (lanzan `NotImplementedError`), a la espera de que se agreguen los campos `role`/`is_premium` al modelo `AuthUser` (ver Sección 12.5).

---

## 10. Capa de Persistencia y Modelos de Datos

### 10.1 Motor de base de datos

`database/client.py` crea un único engine SQLModel/SQLAlchemy a partir de `settings.DATABASE_URL`. `get_session()` es un generador (`with Session(engine) as session: yield session`) usado como `Depends(get_session)`, garantizando una sesión por petición HTTP.

### 10.2 Creación de esquema y migraciones

`main.py` sigue ejecutando `SQLModel.metadata.create_all(engine)` al arrancar. **Alembic sigue declarado en `requirements.txt` pero no configurado** (no existe carpeta `alembic/` ni `alembic.ini`), a pesar de que el modelo de datos ya creció considerablemente (5 tablas). Se recomienda inicializarlo antes de introducir el próximo cambio de esquema en un entorno con datos reales.

### 10.3 Modelo de datos actual

| Tabla | Modelo SQLModel | Rol |
|---|---|---|
| `auth_users` | `AuthUser` | Identidad y credenciales. Ahora incluye `eliminado_en: Optional[date]` para soportar el soft delete y su ventana de reactivación |
| `usuario` | `Usuario` | Datos de negocio del usuario, relación 1:1 con `auth_users` reutilizando `id_usuario` como PK/FK, pensada para crecer (nombre, apellido, etc.) sin ensuciar la tabla de autenticación |
| `sesiones` | `Sesiones` | Una fila por sesión activa: `hash_refresh_token`, `ip`, `user_agent`, `inicio_sesion`, `id_usuario` |
| `recover_password` | `RecoverPassword` | `token_hash`, `expira_en`, `usado`, `id_usuario` |
| `history_password` | `HistoryPassword` | `password_hash_anterior`, `fecha_cambio`, `id_usuario` |

`AuthUser.estado` sigue mapeado a un **ENUM nativo de PostgreSQL** (`estado_entidad`), con `server_default` a nivel de motor.

```python
class EstadoEntidad(str, Enum):
    ACTIVO = 'activo'
    ELIMINADO = 'eliminado'
    REPORTADO = 'reportado'
    SUSPENDIDO = 'suspendido'
    PENDIENTE = 'pendiente'
```

El enum sigue viviendo en `database/enums/` (no en `auth/`), reforzando que está pensado como transversal a futuras entidades más allá de usuarios.

### 10.4 DTOs relevantes

Además de los ya existentes (`UsuarioCreado`, `UserRegisterDTO`, `UserTokens`, `UsuarioLogeado`, `LoginResponse`), se suman:

| Clase | Propósito |
|---|---|
| `UserModifyDTO` | Entrada de `PUT /modificar/usuario` (email opcional) |
| `AuthUserEmailValidation` | DTO auxiliar para revalidar longitud/formato del email dentro de `ModificarUsuarioUseCase` |
| `SesionesVisual` | Proyección pública de una sesión (sin el hash del token), con el flag `es_actual` |
| `ListaSesiones` | Wrapper de `list[SesionesVisual]` para la respuesta de `listar_sesiones` |
| `SolicitudRecuperacionRequest` / `SolicitudReactivacionRequest` | Body de las solicitudes de recuperación/reactivación (`email: EmailStr`, validado por Pydantic antes de llegar al Caso de Uso) |
| `ModificarPassword` | Body del endpoint de cambio de contraseña |

`AuthUserNoImage` sigue presente y sin ninguna referencia activa desde routers o Casos de Uso — probablemente un modelo preparado para un flujo alternativo, no integrado todavía.

### 10.5 Repositorios

`AuthUserRepository` implementa `AuthUserRepositoryProtocol` de forma estructural sobre `session.exec(select(...))`. `obtener_por_email`/`obtener_por_id` siguen filtrando por `estado == ACTIVO`; `obtener_por_id_sin_activar` no filtra (necesario para verificación de mail); y ahora se suman `obtener_usuario_eliminado_por_mail`/`obtener_usuario_eliminado_por_id`, que filtran explícitamente por `estado == ELIMINADO` — el par inverso, necesario para el flujo de reactivación. `SesionRepository.eliminar_todas_las_sesiones_de_un_usuario` usa un `delete()` en bloque de SQLModel, invocado al confirmar la eliminación de cuenta.

---

## 11. Integración de Servicios Externos

### 11.1 Cloudinary (almacenamiento de imágenes)

Sin cambios funcionales respecto a versiones anteriores: `ImageService.subir_imagen()` valida contra `SERVICIOS_VALIDOS`, tamaño (`MAX_FILE_SIZE = 5 MB`) y extensión antes de invocar `cloudinary_uploader.upload(...)`, organizando los archivos bajo `{NOMBRE_APP}/{servicio}`. Ver Sección 14 respecto a un cambio reciente en el manejo de la excepción de servicio inválido.

### 11.2 FastAPI-Mail + Jinja2 (correo electrónico)

`MailService` ahora expone **cuatro generadores de correo**, uno por plantilla (`generar_correo_verificacion`, `generar_correo_recuperacion`, `generar_correo_eliminacion`, `generar_correo_reactivacion`), todos siguiendo el mismo patrón: cargar la plantilla vía `jinja2.Environment(loader=FileSystemLoader(TEMPLATE_DIR))` y renderizarla con la URL correspondiente y `nombre_app`. Las cuatro plantillas comparten el mismo sistema visual (tarjeta oscura, acento de color, sección de "si no fuiste vos ignorá este correo"), diferenciándose por color de acento (violeta para verificación/recuperación/reactivación, rojo para eliminación) e ícono.

---

## 12. Guía del Desarrollador: Cómo extender la plantilla

### 12.1 Agregar un nuevo endpoint a un módulo existente

Sin cambios respecto al flujo original: crear el Caso de Uso, exponerlo en `routers.py` vía `Depends`, sin lógica de negocio en el endpoint.

### 12.2 Agregar un nuevo Caso de Uso

1. Ubicarlo en el subpaquete que corresponda semánticamente (`use_cases/`, o uno de los subpaquetes `sesiones/`, `recover_password/`, `eliminar_usuario/`, `reactivacion_cuenta/`, o uno nuevo si abre un sub-dominio propio).
2. El constructor recibe únicamente Protocolos y Servicios de Dominio.
3. Si la operación toca más de una tabla, envolver los pasos en un bloque `with self.unit_of_work_service:` para que el commit/rollback sea atómico.
4. Crear la clase `ContainerMiCasoDeUso` en `container/auth_container.py` y su `get_mi_caso_de_uso(...)` en `container/providers.py`.
5. Inyectarlo en el router correspondiente.

### 12.3 Agregar una nueva entidad/modelo

Igual que antes: definir el modelo en `infrastructure/persistence/postgres/models/`, reutilizar `EstadoEntidad` si aplica semánticamente, definir DTOs de entrada/salida propios, e inicializar Alembic antes de tocar una base con datos reales (Sección 10.2).

### 12.4 Implementar un nuevo repositorio o servicio (cambiar de proveedor)

Sin cambios en el mecanismo: localizar el `Protocol`, crear la nueva clase en `infrastructure/` cumpliendo su firma, y modificar una sola función factory en `container/providers.py`. Ningún archivo de `domain/` ni `application/` requiere cambios.

### 12.5 Agregar autorización basada en roles (completar `get_admin_user`)

1. Agregar `role: str = Field(default="user")` y/o `is_premium: bool = Field(default=False)` a `AuthUser`.
2. Reemplazar el cuerpo de `get_admin_user`/`get_premium_user` en `guards.py` (actualmente `raise NotImplementedError(...)`) por la validación real, descomentando la lógica ya esbozada en los comentarios del propio archivo.
3. Proteger un endpoint reemplazando `Depends(get_current_user)` por `Depends(get_admin_user)` o `Depends(get_premium_user)`.

### 12.6 Extender el ciclo de vida de la cuenta (nuevo)

El patrón "solicitud por correo → confirmación con token de scope propio → efecto en `estado`" ya está probado en tres flujos (verificación, eliminación, reactivación) y en el flujo de tres pasos de recuperación de contraseña. Para un nuevo estado de cuenta (por ejemplo, "suspensión" con `EstadoEntidad.SUSPENDIDO`, ya presente en el enum pero sin flujo implementado), el camino más consistente con la arquitectura es replicar ese mismo patrón: un método `create_<scope>_token`/`get_user_id_from_<scope>_token` en `TokenProtocol`/`TokenService`, un par de Casos de Uso (solicitud + confirmación), y una plantilla de correo dedicada.

---

## 13. Buenas Prácticas y Patrones de Diseño Aplicados

### 13.1 Principios SOLID — evidencia directa en el código

**Single Responsibility Principle (SRP)**: cada Caso de Uso resuelve un único flujo; `CookiesService` solo gestiona cookies; `MailPolicyService`/`PasswordPolicyService` solo validan una regla cada uno.

**Open/Closed Principle (OCP)**: la jerarquía `DomainError` permite agregar excepciones (`ErrorEliminacion`, `PeriodoReactivacionFinalizado`, etc.) sin tocar el manejador global. Agregar un nuevo proveedor de imágenes o de mail no requiere modificar ningún Caso de Uso.

**Liskov Substitution Principle (LSP)**: cualquier clase que cumpla `TokenProtocol`, `AuthUserRepositoryProtocol` o `TokenRepositoryProtocol` puede sustituir a su implementación actual sin alterar el comportamiento esperado por los Casos de Uso — de hecho, los **fakes de test** (`FakeUserRepository`, `FakeSesionRepository`, etc.) son la prueba viviente de esta sustituibilidad.

**Interface Segregation Principle (ISP)**: los protocolos están segmentados por responsabilidad concreta; `HistoryRepositoryProtocol` y `RecuperarContraseñaProtocol`, por ejemplo, son protocolos angostos y de propósito único, en vez de un único "repositorio god object" para todo lo relacionado a contraseñas.

**Dependency Inversion Principle (DIP)** — pilar central, ahora reforzado por el patrón `UnitOfWorkProtocol`:
```python
class RecuperarContraseñaUseCase:
    def __init__(
        self,
        recuperar_contraseña_repository: RecuperarContraseñaProtocol,  # ← abstracción
        unit_of_work_service: UnitOfWorkProtocol,                      # ← abstracción
        password_service: PasswordProtocol,                            # ← abstracción
        history_contraseña_repository: HistoryRepositoryProtocol,      # ← abstracción
        password_policy: PasswordPolicyService,
        auth_user_repository: AuthUserRepositoryProtocol,               # ← abstracción
    ): ...
```
Ni la unidad de trabajo ni ninguno de los repositorios se referencian por su tipo concreto — el Caso de Uso orquesta una operación que toca tres tablas sin saber si están en PostgreSQL, en memoria (tests) o en cualquier otro motor.

### 13.2 Otros patrones de diseño identificados

- **Repository Pattern**: uno por tabla/agregado (`AuthUserRepository`, `SesionRepository`, `RecoverPasswordRepository`, `HistoryPasswordRepository`, `UserRepository`).
- **Unit of Work**: `UnitOfWork`/`UnitOfWorkProtocol` agrupa operaciones multi-repositorio en una transacción atómica — patrón nuevo respecto a versiones tempranas de la plantilla, y ahora usado en prácticamente todos los Casos de Uso que escriben en base de datos.
- **Dependency Injection (vía FastAPI `Depends`)**: sin frameworks externos de DI.
- **Composition Root**: `container/` sigue siendo el único punto donde Protocolos e implementaciones concretas se encuentran.
- **DTO (Data Transfer Object)**: ahora también `UserModifyDTO`, `SesionesVisual`, `SolicitudRecuperacionRequest`/`SolicitudReactivacionRequest`, `ModificarPassword`.
- **Global Exception Handler**: un único `@app.exception_handler(DomainError)` sigue reemplazando decenas de bloques `try/except` repetidos.
- **Test Doubles estructurales (Fakes/Stubs)**: al ser Protocols, los dobles de test no necesitan heredar de nada — son clases independientes que cumplen la misma firma, lo que hace que la suite de tests (Sección 4.1) sea, en sí misma, una demostración práctica del DIP.

---

## 14. Resumen y Conclusiones Técnicas

### 14.1 Evaluación de robustez y mantenibilidad

El proyecto mantiene la separación de capas que ya lo caracterizaba y la extiende de forma consistente al incorporar seis nuevos flujos de negocio (reenvío de verificación, modificación de perfil, sesiones multi-dispositivo, recuperación de contraseña, eliminación y reactivación de cuenta) sin romper el patrón original: cada flujo nuevo sigue siendo un Caso de Uso que solo conoce Protocolos, cableado por una nueva clase `Container*` y una nueva función `get_*` en `providers.py`. La incorporación del patrón **Unit of Work** es la mejora estructural más significativa de esta iteración: operaciones que antes hubieran quedado implícitamente atómicas por casualidad (una sola escritura) ahora tienen garantías explícitas de todo-o-nada cuando tocan varias tablas (por ejemplo, cambiar una contraseña sin perder la fila de historial si falla la desactivación del token).

### 14.2 Escalabilidad como plantilla reutilizable

El patrón "solicitud por correo con token de scope propio → confirmación → efecto sobre `estado`" quedó consolidado y replicado tres veces (verificación, eliminación, reactivación) además del flujo de tres pasos de recuperación de contraseña — lo que confirma que, más que una plantilla de autenticación, este proyecto ofrece un **framework interno para el ciclo de vida completo de una cuenta**, fácilmente extensible a nuevos estados (por ejemplo, `SUSPENDIDO`, ya presente en el enum) siguiendo exactamente el mismo molde (ver 12.6).

### 14.3 Áreas de mejora detectadas durante la auditoría

Hallazgos que no comprometen el funcionamiento actual de los flujos principales, mantenidos, resueltos o nuevos respecto a la auditoría anterior:

1. **(Resuelto)** La colisión de nombres de excepción `TokenInvalido` entre `domain/exceptions/tokens.py` y `domain/exceptions/usuarios_exceptions.py` ya no existe: esta última dejó de declarar su propia versión.
2. **(Resuelto)** La discrepancia entre la duración anunciada del enlace de verificación y su duración real ya no aplica: `create_verificacion_token` es ahora un scope de token propio (`VERIFY_MAIL_RECUPERACION`), independiente del access token de sesión.
3. **`max_age` de las cookies `access_token`/`refresh_token` sigue hardcodeado** en `CookiesService` en lugar de derivarse de `ACCESS_TOKEN_EXPIRE_MINUTES`/`REFRESH_TOKEN_DURATION` (Sección 9.9) — a diferencia de `set_reset_cookie`, que sí deriva su duración de `Settings`, mostrando que el patrón correcto ya existe en el propio código y solo falta aplicarlo de forma consistente.
4. **Doble unidad para `REACTIVACION_CUENTA`**: el mismo valor de configuración se interpreta como **minutos** al crear el JWT de reactivación (`TokenService.create_reactivacion_token`) y como **días** al calcular la ventana de gracia post-eliminación (`ReactivarUsuarioUseCase`). Con un valor bajo (por ejemplo, `30`), el enlace de reactivación expiraría en 30 minutos mientras la cuenta seguiría siendo reactivable durante 30 días — probablemente no es el comportamiento buscado. Se recomienda separar en dos variables (`REACTIVACION_TOKEN_EXPIRE_MINUTES` y `REACTIVACION_CUENTA_DIAS`, por ejemplo).
5. **`EXPIRACION_MAIL_RECUPERACION` es una variable declarada pero no consumida** por ningún módulo — configuración muerta que puede inducir a error a quien intente usarla creyendo que gobierna algo.
6. **`VERIFY_MAIL_RECUPERACION` gobierna dos flujos distintos** (verificación de mail y recuperación de contraseña) bajo un nombre que solo referencia a uno de ellos explícitamente, lo cual puede confundir a la hora de ajustar tiempos de expiración de forma independiente para cada flujo.
7. **`ImageService.subir_imagen()` construye `DomainError` con un argumento `detail=...`** para el caso de servicio inválido, pero `DomainError.__init__` espera `message` como primer parámetro posicional — esta rama fallaría con un `TypeError` en tiempo de ejecución en lugar de propagar el error de dominio esperado. Se recomienda corregir a `DomainError(message=f"...")`.
8. **Endpoint `GET /solicitud/reactivacion/cuenta` recibe un body** (`SolicitudReactivacionRequest`) pese a estar declarado como `GET`, lo cual no es idiomático en HTTP/REST (muchos clientes y proxies no garantizan el envío de body en peticiones `GET`). Se recomienda cambiarlo a `POST`, igual que su análogo `POST /solicitud/recuperacion`.
9. **Guards `get_admin_user`/`get_premium_user`** siguen siendo un placeholder explícito (`NotImplementedError`) a la espera de que se agreguen `role`/`is_premium` al modelo `AuthUser` (Sección 6.6/12.5).
10. **Funciones factory duplicadas** (`get_password_service`, `get_token_service`, `get_mail_service`, `get_image_service`) siguen definidas tanto dentro de `infrastructure/` como en `container/providers.py`, sin uso real de las primeras.
11. **Ausencia de configuración activa de Alembic** pese a estar en `requirements.txt`, ahora con un esquema de 5 tablas relacionadas — más urgente de resolver que en la versión anterior.
12. **Typo heredado en `HisoryPasswordNoTable`** (falta una "t": debería ser `HistoryPasswordNoTable`), sin impacto funcional al no estar referenciada activamente, pero visible en el código fuente.
13. **Sin invalidación proactiva de access tokens** ante eliminación de cuenta o cambio de contraseña: `EliminarUsuarioUseCase` y `RecuperarContraseñaUseCase` revocan sesiones (refresh tokens) pero un access token de corta duración ya emitido seguirá siendo técnicamente válido hasta su expiración natural — comportamiento esperado en JWT *stateless*, aceptable dado que la ventana de exposición es corta (`ACCESS_TOKEN_EXPIRE_MINUTES`), pero a tener en cuenta si se requiere revocación inmediata total.

### 14.4 Conclusión general

Esta iteración de la plantilla pasa de cubrir el ciclo básico de "registro → verificación → login → sesión" a cubrir el **ciclo de vida completo de una cuenta de usuario**, incluyendo su recuperación ante pérdida de contraseña, su gestión multi-dispositivo, su baja reversible y su reactivación — todo ello sin desviarse del compromiso arquitectónico original: Protocolos como frontera de dominio, Casos de Uso desacoplados, un Composition Root explícito y, ahora, una Unidad de Trabajo que garantiza consistencia transaccional en las operaciones que lo requieren. Los hallazgos de la Sección 14.3 son, en su mayoría, ajustes de configuración y de nomenclatura de bajo riesgo (con la excepción del bug de `DomainError(detail=...)`, que sí debería corregirse antes de depender de esa ruta de código en producción); ninguno compromete la solidez del diseño de capas que sigue siendo la principal fortaleza de este proyecto como plantilla reutilizable.