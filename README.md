# 🔐 FastAPI Authentication Boilerplate — Object-Oriented Edition

> **PostgreSQL · JWT · Argon2 · Cloudinary · FastAPI-Mail**

Una **plantilla base profesional y opinada** para sistemas de autenticación, autorización y gestión de usuarios en aplicaciones backend con **FastAPI** y **PostgreSQL**. Construida sobre principios de **Clean Architecture** y **Programación Orientada a Objetos**, esta plantilla elimina la lógica repetitiva del manejo de sesiones, permitiendo iniciarse en proyectos con una arquitectura sólida, mantenible y escalable en cuestión de minutos.

A diferencia de muchas plantillas que entremezclan el framework con la lógica de negocio, este proyecto mantiene una **separación clara entre capas**: las clases de dominio no conocen FastAPI, lo que resulta en código más testeable, reutilizable y preparado para evolucionar.

---

## 📋 Tabla de Contenido

1. [Características Principales](#características-principales)
2. [Filosofía del Proyecto](#filosofía-del-proyecto)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Principios de Diseño](#principios-de-diseño)
7. [Inyección de Dependencias](#inyección-de-dependencias)
8. [Instalación y Configuración](#instalación-y-configuración)
9. [Variables de Entorno](#variables-de-entorno)
10. [Descripción Detallada de Módulos](#descripción-detallada-de-módulos)
11. [Servicios — Lógica de Negocio](#servicios--lógica-de-negocio)
12. [Repositorios — Acceso a Datos](#repositorios--acceso-a-datos)
13. [Routers — Capa HTTP](#routers--capa-http)
14. [Endpoints Disponibles](#endpoints-disponibles)
15. [Ejemplos de Uso](#ejemplos-de-uso)
16. [Extensibilidad y Futuras Mejoras](#extensibilidad-y-futuras-mejoras)
17. [Notas de Personalización](#notas-de-personalización)
18. [Contribución y Licencia](#contribución-y-licencia)

---

## Características Principales

| Característica | Descripción |
|---|---|
| 🏗️ **Arquitectura Orientada a Objetos** | Diseño limpio basado en principios SOLID y Clean Architecture |
| 🔒 **Autenticación Segura** | JWT con access tokens de corta duración y refresh tokens de larga duración |
| 🛡️ **Hashing Robusto** | Contraseñas encriptadas con Argon2, el algoritmo más seguro de la industria |
| ✉️ **Verificación por Email** | Flujo completo de validación de cuenta mediante correo electrónico con plantillas HTML |
| 🗄️ **Base de Datos Relacional** | PostgreSQL con ORM moderno (SQLModel/SQLAlchemy) y migraciones versionadas (Alembic) |
| 🖼️ **Gestión de Imágenes** | Integración seamless con Cloudinary para almacenamiento optimizado en la nube |
| 🧩 **Bajo Acoplamiento** | Componentes independientes y reutilizables, fácil de testear sin la necesidad de FastAPI |
| ⚙️ **Configuración Centralizada** | Variables de entorno tipadas y validadas con Pydantic Settings |
| 🔄 **Inyección de Dependencias** | FastAPI construye automáticamente el árbol de dependencias manteniendo las clases desacopladas |
| 📦 **Listo para Escalar** | Estructura preparada para agregar autenticación OAuth2, roles, permisos, caching y eventos |

---

## Filosofía del Proyecto

Esta plantilla nace de una convicción fundamental: **el código de dominio no debe conocer el framework**.

### Los Tres Pilares

#### 1. **Separación de Responsabilidades**
Cada componente tiene una única razón para cambiar. Un servicio orquesta la lógica de negocio, un repositorio maneja datos, un router transforma HTTP en llamadas a servicios. Cuando necesites cambiar la lógica de autenticación, sabes exactamente dónde hacerlo.

#### 2. **Desacoplamiento del Framework**
FastAPI es una herramienta extraordinaria para exponer una API HTTP, pero no debe contaminar el código de negocio. En esta plantilla:

- Las clases de servicios **no importan** `Depends`, `Request`, `Response` o `APIRouter`
- Las clases de repositorios **no conocen** SQL directamente; usan un ORM tipado
- Los routers son **delgados y delegadores**, no contienen lógica

Esto significa que tus servicios y repositorios pueden ser reutilizados en otros contextos: scripts, colas de trabajo (Celery), GraphQL, gRPC, o incluso ser portados a otro framework sin modificación.

#### 3. **Composición sobre Herencia**
Los servicios se construyen componiendo otros servicios más simples. En lugar de largas cadenas de herencia, inyectas las dependencias que necesitas en el constructor y trabajas con ellas. Esto resulta en código más flexible y fácil de testear.

### Por Qué Importa

```
Código Acoplado          →  Código Desacoplado
├─ Difícil de testear   │  └─ Fácil de testear
├─ Cambios requieren    │     └─ Cambios localizados
│  modificaciones múlt. │
├─ Reutilización limitada   └─ Código reutilizable
└─ Deuda técnica            └─ Escalable a largo plazo
```

---

## Tecnologías Utilizadas

| Tecnología | Rol | Versión |
|---|---|---|
| **[FastAPI](https://fastapi.tiangolo.com/)** | Framework web asíncrono de alto rendimiento | ≥ 0.100.0 |
| **[SQLModel](https://sqlmodel.tiangolo.com/)** | ORM moderno que combina SQLAlchemy y Pydantic | ≥ 0.0.8 |
| **[SQLAlchemy](https://www.sqlalchemy.org/)** | SQL Toolkit y ORM pythónico | ≥ 2.0 |
| **[Alembic](https://alembic.sqlalchemy.org/)** | Control de versiones y migraciones de esquema | ≥ 1.10 |
| **[PostgreSQL](https://www.postgresql.org/)** | Motor de base de datos relacional de producción | ≥ 12 |
| **[Argon2](https://argon2-cffi.readthedocs.io/)** | Algoritmo de hash de contraseñas resistente a ataques | ≥ 21.3.0 |
| **[Python-JOSE](https://python-jose.readthedocs.io/)** | Implementación de JWT moderna y segura | ≥ 3.3.0 |
| **[Cloudinary](https://cloudinary.com/documentation/python_sdk)** | Plataforma de gestión y transformación de imágenes | ≥ 1.30.0 |
| **[FastAPI-Mail](https://sabuhish.github.io/fastapi-mail/)** | Soporte asíncrono para envío de emails | ≥ 1.2.0 |
| **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** | Gestión tipada de configuración | ≥ 2.0 |
| **[Python](https://www.python.org/)** | Lenguaje de programación | ≥ 3.10 |

---

## Arquitectura de Alto Nivel

### Diagrama de Flujo de Dependencias

```
┌─────────────────────────────────────────────────────────────┐
│  HTTP Request Layer (Routers)                               │
│  ├─ POST /usuarios/registrar                                │
│  ├─ POST /usuarios/login                                    │
│  └─ GET /usuarios/perfil                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Service Orchestration Layer (Servicios)                    │
│  ├─ AuthService (orquestrador principal)                    │
│  │  ├─ TokenService (manejo de JWT)                         │
│  │  ├─ PasswordService (hash y verificación)                │
│  │  └─ EmailService (notificaciones)                        │
│  └─ Estos servicios coordinan la lógica de negocio          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Data Access Layer (Repositorios)                           │
│  ├─ UserRepository (CRUD de usuarios)                       │
│  └─ Encapsula todas las queries SQL (via ORM)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Database Layer (PostgreSQL)                                │
│  └─ Datos persistentes                                      │
└─────────────────────────────────────────────────────────────┘
```

### Responsabilidades por Capa

#### **Routers (Capa HTTP)**
- Reciben solicitudes HTTP y extraen parámetros
- **NO** contienen lógica de negocio
- Llaman a servicios y transforman respuestas
- Manejan errores HTTP (400, 401, 500)

```python
@router.post("/login")
async def login(
    credentials: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        result = auth_service.login(
            credentials.email,
            credentials.password
        )
        return {"access_token": result.access_token}
    except InvalidCredentialsError:
        raise HTTPException(status_code=401)
```

#### **Servicios (Lógica de Negocio)**
- Orquestan la lógica compleja
- Deciden qué hacer basándose en reglas de negocio
- Coordinan múltiples repositorios y servicios
- **Nunca importan** elementos de FastAPI

```python
class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
        password_service: PasswordService
    ):
        self.user_repo = user_repo
        self.token_service = token_service
        self.password_service = password_service
    
    def login(self, email: str, password: str) -> LoginResult:
        user = self.user_repo.find_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        
        if not self.password_service.verify(password, user.hashed_password):
            raise InvalidCredentialsError()
        
        access_token = self.token_service.create_access_token(user.id)
        return LoginResult(access_token=access_token)
```

#### **Repositorios (Acceso a Datos)**
- Encapsulan todas las operaciones de base de datos
- Responsables únicamente de persistencia
- No contienen lógica de negocio
- Usan ORM tipado

```python
class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def find_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(
            User.email == email
        ).first()
    
    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user
```

---

## Estructura del Proyecto

```
authentication-boilerplate/
│
├── .env                              # Variables de entorno (NO en git)
├── .gitignore
├── requirements.txt                  # Dependencias Python
├── pyproject.toml                    # Metadatos del proyecto
├── README.md                         # Este archivo
│
├── alembic/                          # Control de migraciones
│   ├── versions/                     # Archivos de migración versionados
│   ├── env.py
│   └── alembic.ini
│
└── src/
    │
    ├── main.py                       # Punto de entrada de la aplicación
    │
    ├── config/
    │   └── settings.py               # Configuración centralizada (Pydantic)
    │
    ├── database/
    │   ├── connection.py             # Conexión a PostgreSQL
    │   └── session.py                # SessionLocal y dependency para FastAPI
    │
    ├── auth/
    │   ├── models/
    │   │   └── user.py               # Modelo SQLModel del usuario
    │   │
    │   ├── schemas/
    │   │   └── user_schema.py        # Esquemas Pydantic (entrada/salida)
    │   │
    │   ├── repositories/
    │   │   └── user_repository.py    # Acceso a datos de usuario
    │   │
    │   ├── services/
    │   │   ├── token_service.py      # Creación y validación de JWT
    │   │   ├── password_service.py   # Hash y verificación de contraseñas
    │   │   ├── email_service.py      # Envío de correos
    │   │   └── auth_service.py       # Orquestrador principal
    │   │
    │   ├── dependencies/
    │   │   └── dependencies.py       # Dependencias de FastAPI (factories)
    │   │
    │   └── routers/
    │       └── auth_router.py        # Endpoints HTTP
    │
    ├── cloudinary/
    │   └── image_service.py          # Lógica de gestión de imágenes
    │
    ├── exceptions/
    │   └── auth_exceptions.py        # Excepciones de dominio
    │
    ├── templates/
    │   └── email_verification.html   # Plantilla HTML de verificación
    │
    └── utils/
        └── validators.py             # Funciones de validación
```

---

## Principios de Diseño

### 1. Single Responsibility Principle (SRP)

Cada clase tiene una única razón para cambiar. Un servicio no debería gestionar conexiones a base de datos; un repositorio no debería calcular hashes.

```python
# ❌ MAL: TokenService hace demasiadas cosas
class BadTokenService:
    def create_token(self, user_id):
        # Conecta a base de datos
        # Genera el token
        # Envia email
        # Registra en logs
        pass

# ✅ BIEN: Cada clase tiene una responsabilidad
class TokenService:
    def create_token(self, user_id: str) -> str:
        payload = {"sub": user_id, "exp": ...}
        return jwt.encode(payload, self.secret)

class EmailService:
    def send_verification_email(self, email: str, token: str):
        # Solo envía emails
        pass
```

### 2. Open/Closed Principle (OCP)

Las clases deben estar abiertas para extensión, cerradas para modificación. Cuando necesites soportar un nuevo tipo de servicio, hazlo mediante herencia o composición, no modificando la clase existente.

```python
# Abierto para extensión
class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        pass

class Argon2Hasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return argon2.hash(password)

class BcryptHasher(PasswordHasher):  # Nueva implementación
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password)

# Cerrado para modificación
class PasswordService:
    def __init__(self, hasher: PasswordHasher):
        self.hasher = hasher
    
    def hash_password(self, plain: str) -> str:
        return self.hasher.hash(plain)
```

### 3. Dependency Inversion Principle (DIP)

Las clases de alto nivel no deben depender de clases de bajo nivel; ambas deben depender de abstracciones.

```python
# ❌ MAL: Acoplamiento directo
class AuthService:
    def __init__(self):
        self.db_session = SessionLocal()  # Acoplado a implementación
        self.user_repo = UserRepository(self.db_session)

# ✅ BIEN: Inyección de dependencias
class AuthService:
    def __init__(
        self,
        user_repo: UserRepository  # Solo necesita la abstracción
    ):
        self.user_repo = user_repo
```

### 4. Encapsulación

Los detalles internos de una clase deben ser privados. Expón solo lo que sea necesario.

```python
class TokenService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._secret = settings.jwt_secret_key  # Privado
        self._algorithm = settings.jwt_algorithm  # Privado
    
    def create_access_token(self, user_id: str) -> str:
        """Crea un token de acceso firmado."""
        return self._generate_token(user_id, self._get_expiration())
    
    def _generate_token(self, user_id: str, exp: int) -> str:
        """Método privado para generar el token."""
        payload = {"sub": user_id, "exp": exp}
        return jwt.encode(payload, self._secret, self._algorithm)
    
    def _get_expiration(self) -> int:
        """Calcula el tiempo de expiración."""
        return int(time.time()) + (self.settings.access_token_expire_minutes * 60)
```

### 5. Composición sobre Herencia

```python
# ❌ MAL: Herencia profunda
class BaseService:
    pass

class AuthServiceBase(BaseService):
    pass

class UserManagementService(AuthServiceBase):
    pass

# ✅ BIEN: Composición
class AuthService:
    def __init__(
        self,
        token_service: TokenService,
        password_service: PasswordService,
        email_service: EmailService,
        user_repo: UserRepository
    ):
        self.token_service = token_service
        self.password_service = password_service
        self.email_service = email_service
        self.user_repo = user_repo
```

---

## Inyección de Dependencias

FastAPI proporciona un sistema de inyección de dependencias poderoso. En esta plantilla, lo usamos estratégicamente para mantener las clases desacopladas del framework.

### Cómo Funciona

```
1. Router Declara Dependencia
   ↓
2. FastAPI Inspecciona el Tipo
   ↓
3. FastAPI Busca la Función Factory
   ↓
4. Factory Resuelve Dependencias Recursivas
   ↓
5. Factory Retorna Instancia Completamente Inicializada
   ↓
6. Router Recibe la Instancia Inyectada
```

### Ejemplo Práctico

```python
# 1. SERVICIOS (Sin conocimiento de FastAPI)
class TokenService:
    def __init__(self, settings: Settings):
        self.settings = settings

class PasswordService:
    def __init__(self, settings: Settings):
        self.settings = settings

class AuthService:
    def __init__(
        self,
        token_service: TokenService,
        password_service: PasswordService,
        user_repo: UserRepository
    ):
        self.token_service = token_service
        self.password_service = password_service
        self.user_repo = user_repo

# 2. FACTORIES (Funciones que crean las instancias)
def get_token_service(
    settings: Settings = Depends(get_settings)
) -> TokenService:
    return TokenService(settings)

def get_password_service(
    settings: Settings = Depends(get_settings)
) -> PasswordService:
    return PasswordService(settings)

def get_auth_service(
    token_service: TokenService = Depends(get_token_service),
    password_service: PasswordService = Depends(get_password_service),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(token_service, password_service, user_repo)

# 3. ROUTER (Delgado y limpio)
@router.post("/login")
async def login(
    credentials: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    result = auth_service.login(credentials.email, credentials.password)
    return {"access_token": result.access_token}
```

### Árbol de Dependencias Automático

FastAPI construye automáticamente el árbol:

```
Router Endpoint
  └─ AuthService
      ├─ TokenService
      │   └─ Settings
      ├─ PasswordService
      │   └─ Settings
      ├─ UserRepository
      │   └─ Session (conexión a BD)
      └─ ...
```

Incluso si `AuthService` necesita que `TokenService` necesita `Settings`, FastAPI se encarga de todo. Solo declara la dependencia más profunda en una función factory y FastAPI la resuelve completamente.

---

## Instalación y Configuración

### Prerequisitos

- Python 3.10 o superior
- PostgreSQL 12 o superior
- pip o poetry para gestión de dependencias
- Git para control de versiones

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tuusuario/authentication-boilerplate.git
cd authentication-boilerplate
```

### Paso 2: Crear Entorno Virtual

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

O si usas Poetry:

```bash
poetry install
```

### Paso 4: Configurar Base de Datos

Crear una base de datos PostgreSQL:

```sql
CREATE DATABASE authentication_db;
```

### Paso 5: Crear Archivo `.env`

Copiar `.env.example` a `.env` y rellenar los valores (ver sección siguiente).

### Paso 6: Ejecutar Migraciones

```bash
# Crear todas las tablas
alembic upgrade head
```

### Paso 7: Iniciar la Aplicación

```bash
uvicorn src.main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`

Documentación interactiva:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Variables de Entorno

Las variables de entorno se cargan automáticamente desde el archivo `.env` usando Pydantic Settings. Todas las variables son **tipadas y validadas** automáticamente.

### Base de Datos

```env
# Conexión a PostgreSQL
# Formato: postgresql+psycopg://usuario:contraseña@host:puerto/base_datos
DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5432/auth_db"
```

| Variable | Tipo | Descripción |
|---|---|---|
| `DATABASE_URL` | `str` | Cadena de conexión a PostgreSQL con psycopg3 |

### JWT - Autenticación

```env
JWT_SECRET_KEY="tu-clave-super-secreta-muy-larga-y-aleatoria-min-32-chars"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

| Variable | Tipo | Rango | Descripción |
|---|---|---|---|
| `JWT_SECRET_KEY` | `str` | ≥ 32 chars | Clave secreta para firmar tokens JWT |
| `JWT_ALGORITHM` | `str` | `HS256`, `HS512` | Algoritmo de firma |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | > 0 | Duración del access token (ej: 30 min) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `int` | > 0 | Duración del refresh token (ej: 7 días) |

### Correo Electrónico

```env
MAIL_SMTP_SERVER="smtp.gmail.com"
MAIL_SMTP_PORT=587
MAIL_USERNAME="tu-email@gmail.com"
MAIL_PASSWORD="contraseña-de-aplicacion"
MAIL_FROM_NAME="Tu Aplicación"
MAIL_FROM_ADDRESS="noreply@tuapp.com"
MAIL_USE_TLS=true
```

| Variable | Tipo | Descripción |
|---|---|---|
| `MAIL_SMTP_SERVER` | `str` | Servidor SMTP (ej: smtp.gmail.com) |
| `MAIL_SMTP_PORT` | `int` | Puerto SMTP (587 para TLS, 465 para SSL) |
| `MAIL_USERNAME` | `str` | Usuario/email para autenticación SMTP |
| `MAIL_PASSWORD` | `str` | Contraseña de aplicación (no contraseña principal) |
| `MAIL_FROM_NAME` | `str` | Nombre que aparece en el "De:" del email |
| `MAIL_FROM_ADDRESS` | `str` | Email que aparece en el "De:" |
| `MAIL_USE_TLS` | `bool` | Usar TLS (recomendado para seguridad) |

> 💡 **Para Gmail**: Habilita [Contraseñas de Aplicación](https://support.google.com/accounts/answer/185833) en tu cuenta Google.

### Cloudinary - Gestión de Imágenes

```env
CLOUDINARY_CLOUD_NAME="tu_cloud_name"
CLOUDINARY_API_KEY="tu_api_key"
CLOUDINARY_API_SECRET="tu_api_secret"
CLOUDINARY_UPLOAD_PRESET="usuarios"
```

| Variable | Tipo | Descripción |
|---|---|---|
| `CLOUDINARY_CLOUD_NAME` | `str` | Nombre único de tu cuenta Cloudinary |
| `CLOUDINARY_API_KEY` | `str` | Clave pública de la API |
| `CLOUDINARY_API_SECRET` | `str` | Clave privada de la API (mantener segura) |
| `CLOUDINARY_UPLOAD_PRESET` | `str` | Preset de carga (carpeta virtual para organizar) |

### Aplicación

```env
APP_NAME="Mi Aplicación"
APP_VERSION="1.0.0"
API_PREFIX="/api/v1"
ENVIRONMENT="development"
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

| Variable | Tipo | Valores | Descripción |
|---|---|---|---|
| `APP_NAME` | `str` | Cualquiera | Nombre de la aplicación |
| `APP_VERSION` | `str` | Semver | Versión actual (ej: 1.0.0) |
| `API_PREFIX` | `str` | Cualquiera | Prefijo de rutas (ej: /api/v1) |
| `ENVIRONMENT` | `str` | `development`, `production` | Entorno actual |
| `DEBUG` | `bool` | `true`, `false` | Habilitar modo debug |
| `ALLOWED_ORIGINS` | `list[str]` | URLs | Dominios permitidos (CORS) |

### Ejemplo Completo de `.env`

```env
# =====================
# Base de Datos
# =====================
DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5432/auth_db"

# =====================
# JWT
# =====================
JWT_SECRET_KEY="dev-secret-key-min-32-chars-required-here-12345"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =====================
# Email (Gmail)
# =====================
MAIL_SMTP_SERVER="smtp.gmail.com"
MAIL_SMTP_PORT=587
MAIL_USERNAME="myapp@gmail.com"
MAIL_PASSWORD="abcd efgh ijkl mnop"
MAIL_FROM_NAME="Mi Aplicación"
MAIL_FROM_ADDRESS="noreply@miapp.com"
MAIL_USE_TLS=true

# =====================
# Cloudinary
# =====================
CLOUDINARY_CLOUD_NAME="my_cloud"
CLOUDINARY_API_KEY="123456789012345"
CLOUDINARY_API_SECRET="abc123xyz456def789ghi"
CLOUDINARY_UPLOAD_PRESET="usuarios"

# =====================
# Aplicación
# =====================
APP_NAME="Authentication Boilerplate"
APP_VERSION="1.0.0"
API_PREFIX="/api/v1"
ENVIRONMENT="development"
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

---

## Descripción Detallada de Módulos

### `src/main.py` — Punto de Entrada

Inicializa la aplicación FastAPI, registra routers, configura middlewares y establece la documentación.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import Settings
from src.auth.routers import auth_router

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Autenticación con JWT y PostgreSQL"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth_router, prefix=settings.api_prefix)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### `src/config/settings.py` — Configuración Centralizada

Modelo Pydantic que lee y valida automáticamente todas las variables de entorno. Proporciona validaciones en tiempo de inicio (fail-fast).

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Base de datos
    database_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Email
    mail_smtp_server: str
    mail_smtp_port: int
    mail_username: str
    mail_password: str
    mail_from_name: str
    mail_from_address: str
    mail_use_tls: bool = True
    
    # Cloudinary
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_upload_preset: str
    
    # Aplicación
    app_name: str = "Authentication API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = False
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

### `src/database/` — Gestión de Base de Datos

#### `connection.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import Settings

settings = Settings()

engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL en desarrollo
    pool_pre_ping=True,  # Verificar conexión antes de usar
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_session():
    """Generator para inyectar sesión en endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### `src/auth/models/user.py` — Modelo de Usuario

Define la estructura de datos del usuario en la base de datos usando SQLModel.

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # Identificadores
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Datos principales
    email: str = Field(unique=True, index=True)
    hashed_password: str
    
    # Perfil
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Estado
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    
    # Auditoría
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
```

---

### `src/auth/schemas/user_schema.py` — Esquemas Pydantic

Define las estructuras de datos para entrada y salida de endpoints.

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserProfileSchema(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    profile_picture_url: Optional[str]
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Convertir ORM a Pydantic
```

---

## Servicios — Lógica de Negocio

### TokenService

Responsable de **toda la lógica JWT**: creación, validación y decodificación de tokens.

```python
from datetime import datetime, timedelta
import jwt
from src.config.settings import Settings
from src.exceptions.auth_exceptions import InvalidTokenError

class TokenService:
    """Servicio de gestión de tokens JWT."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
    
    def create_access_token(self, user_id: int) -> str:
        """Crea un access token de corta duración."""
        expiration = datetime.utcnow() + timedelta(
            minutes=self.settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "exp": expiration,
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Crea un refresh token de larga duración."""
        expiration = datetime.utcnow() + timedelta(
            days=self.settings.refresh_token_expire_days
        )
        payload = {
            "sub": str(user_id),
            "exp": expiration,
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, self.algorithm)
    
    def decode_token(self, token: str) -> dict:
        """Decodifica y valida un token."""
        try:
            payload = jwt.decode(token, self.secret_key, self.algorithm)
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Token inválido")
            return {"user_id": int(user_id), "payload": payload}
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token expirado")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Token inválido")
    
    def is_token_expired(self, token: str) -> bool:
        """Verifica si un token está expirado."""
        try:
            self.decode_token(token)
            return False
        except InvalidTokenError:
            return True
```

### PasswordService

Responsable del hash y verificación segura de contraseñas.

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from src.exceptions.auth_exceptions import InvalidPasswordError

class PasswordService:
    """Servicio de seguridad de contraseñas."""
    
    def __init__(self):
        self.hasher = PasswordHasher()
    
    def hash_password(self, plain_password: str) -> str:
        """Genera un hash Argon2 de la contraseña."""
        try:
            return self.hasher.hash(plain_password)
        except Exception as e:
            raise InvalidPasswordError(f"Error al hashear contraseña: {str(e)}")
    
    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verifica que una contraseña coincida con su hash."""
        try:
            self.hasher.verify(hashed_password, plain_password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Valida que la contraseña cumpla estándares mínimos de seguridad.
        
        Retorna: (es_válida, mensaje_error)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener mayúsculas"
        
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener números"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "La contraseña debe contener caracteres especiales"
        
        return True, "Contraseña válida"
```

### EmailService

Responsable del envío de correos de verificación y notificaciones.

```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template
from src.config.settings import Settings
from src.exceptions.auth_exceptions import EmailSendError

class EmailService:
    """Servicio de envío de correos electrónicos."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.config = ConnectionConfig(
            mail_from=settings.mail_from_address,
            mail_password=settings.mail_password,
            mail_port=settings.mail_smtp_port,
            mail_server=settings.mail_smtp_server,
            mail_starttls=settings.mail_use_tls,
            mail_ssl_tls=False,
            use_credentials=True,
            validate_certs=True,
        )
        self.fm = FastMail(self.config)
    
    async def send_verification_email(
        self,
        email: str,
        verification_token: str,
        app_name: str
    ) -> bool:
        """Envía el email de verificación de cuenta."""
        try:
            verification_url = (
                f"{self.settings.base_url}/verify-email"
                f"?token={verification_token}"
            )
            
            html_template = """
            <html>
                <body>
                    <h1>Bienvenido a {app_name}</h1>
                    <p>Haz click en el siguiente enlace para verificar tu cuenta:</p>
                    <a href="{verification_url}">Verificar cuenta</a>
                </body>
            </html>
            """
            
            html = Template(html_template).render(
                app_name=app_name,
                verification_url=verification_url
            )
            
            message = MessageSchema(
                subject=f"Verificación de cuenta - {app_name}",
                recipients=[email],
                body=html,
                subtype="html"
            )
            
            await self.fm.send_message(message)
            return True
            
        except Exception as e:
            raise EmailSendError(f"Error al enviar email: {str(e)}")
```

### AuthService

Orquestrador principal que coordina toda la lógica de autenticación.

```python
from src.auth.repositories.user_repository import UserRepository
from src.auth.services.token_service import TokenService
from src.auth.services.password_service import PasswordService
from src.auth.services.email_service import EmailService
from src.auth.models.user import User
from src.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError
)

class AuthService:
    """Servicio de autenticación - orquestrador principal."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
        password_service: PasswordService,
        email_service: EmailService
    ):
        self.user_repo = user_repository
        self.token_service = token_service
        self.password_service = password_service
        self.email_service = email_service
    
    def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str
    ) -> dict:
        """
        Registra un nuevo usuario.
        
        Flujo:
        1. Verifica que el usuario no exista
        2. Valida la contraseña
        3. Hashea la contraseña
        4. Crea el usuario en base de datos
        5. Envia correo de verificación
        6. Retorna la información del usuario
        """
        # Verificar que el usuario no existe
        if self.user_repo.find_by_email(email):
            raise UserAlreadyExistsError(f"Email {email} ya registrado")
        
        # Validar fortaleza de contraseña
        is_valid, message = self.password_service.validate_password_strength(password)
        if not is_valid:
            raise InvalidCredentialsError(message)
        
        # Hashear contraseña
        hashed_password = self.password_service.hash_password(password)
        
        # Crear usuario
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        user = self.user_repo.create(new_user)
        
        # Crear token de verificación
        verification_token = self.token_service.create_access_token(user.id)
        
        # Enviar email
        try:
            asyncio.run(self.email_service.send_verification_email(
                email=email,
                verification_token=verification_token,
                app_name="Mi Aplicación"
            ))
        except Exception as e:
            # Log pero no fallar el registro
            print(f"Error enviando email: {e}")
        
        return {
            "user_id": user.id,
            "email": user.email,
            "message": "Usuario registrado. Revisa tu correo para verificar."
        }
    
    def login(self, email: str, password: str) -> dict:
        """
        Autentica un usuario y retorna tokens.
        
        Flujo:
        1. Busca el usuario por email
        2. Verifica la contraseña
        3. Crea access y refresh tokens
        4. Retorna los tokens
        """
        # Buscar usuario
        user = self.user_repo.find_by_email(email)
        if not user:
            raise InvalidCredentialsError("Email o contraseña incorrectos")
        
        # Verificar contraseña
        if not self.password_service.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Email o contraseña incorrectos")
        
        # Verificar que el usuario está activo
        if not user.is_active:
            raise InvalidCredentialsError("Cuenta desactivada")
        
        # Crear tokens
        access_token = self.token_service.create_access_token(user.id)
        refresh_token = self.token_service.create_refresh_token(user.id)
        
        # Actualizar último login
        self.user_repo.update_last_login(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Genera un nuevo access token usando el refresh token."""
        try:
            token_data = self.token_service.decode_token(refresh_token)
            user_id = token_data["user_id"]
            
            # Verificar que el usuario existe y está activo
            user = self.user_repo.find_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidCredentialsError("Usuario no válido")
            
            # Crear nuevo access token
            new_access_token = self.token_service.create_access_token(user_id)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        except Exception as e:
            raise InvalidCredentialsError(f"Token de refresco inválido: {str(e)}")
    
    def verify_email(self, verification_token: str) -> dict:
        """Verifica la cuenta del usuario usando el token."""
        try:
            token_data = self.token_service.decode_token(verification_token)
            user_id = token_data["user_id"]
            
            user = self.user_repo.find_by_id(user_id)
            if not user:
                raise UserNotFoundError("Usuario no encontrado")
            
            # Marcar como verificado
            user.is_verified = True
            self.user_repo.update(user)
            
            return {"message": "Email verificado correctamente"}
            
        except Exception as e:
            raise InvalidCredentialsError(f"Token inválido: {str(e)}")
```

---

## Repositorios — Acceso a Datos

### UserRepository

Encapsula toda la lógica de acceso a datos de usuarios. No contiene lógica de negocio.

```python
from sqlalchemy.orm import Session
from src.auth.models.user import User
from src.exceptions.auth_exceptions import UserNotFoundError
from typing import Optional

class UserRepository:
    """Repositorio para acceso a datos de usuarios."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user: User) -> User:
        """Crea un nuevo usuario en la base de datos."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por ID."""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email."""
        return self.session.query(User).filter(User.email == email).first()
    
    def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Retorna todos los usuarios con paginación."""
        return self.session.query(User).offset(skip).limit(limit).all()
    
    def update(self, user: User) -> User:
        """Actualiza un usuario existente."""
        self.session.merge(user)
        self.session.commit()
        return user
    
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario por ID."""
        user = self.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario {user_id} no encontrado")
        
        self.session.delete(user)
        self.session.commit()
        return True
    
    def update_last_login(self, user_id: int) -> None:
        """Actualiza la fecha del último login."""
        from datetime import datetime
        user = self.find_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            self.update(user)
```

---

## Routers — Capa HTTP

### auth_router.py

Define los endpoints HTTP. Extremadamente delgado, solo recibe requests y delega a servicios.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from src.auth.schemas.user_schema import (
    UserRegisterSchema,
    UserLoginSchema,
    UserProfileSchema
)
from src.auth.services.auth_service import AuthService
from src.auth.dependencies.dependencies import (
    get_auth_service,
    get_current_user
)
from src.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError
)
from src.auth.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", status_code=201)
async def register(
    user_data: UserRegisterSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Registra un nuevo usuario.
    
    Retorna:
    - user_id: ID del usuario creado
    - email: Email del usuario
    - message: Instrucciones para verificar
    """
    try:
        result = auth_service.register(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        return result
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login(
    credentials: UserLoginSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Autentica un usuario y retorna access/refresh tokens en cookies.
    
    Retorna:
    - access_token: Token de acceso JWT
    - refresh_token: Token para renovar sesión
    - token_type: Tipo de token (bearer)
    """
    try:
        result = auth_service.login(
            email=credentials.email,
            password=credentials.password
        )
        
        response = JSONResponse(content={
            "access_token": result["access_token"],
            "token_type": "bearer"
        })
        
        # Guardar tokens en cookies secure
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800  # 30 minutos
        )
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=604800  # 7 días
        )
        
        return response
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

@router.get("/profile", response_model=UserProfileSchema)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Retorna el perfil del usuario autenticado."""
    return current_user

@router.post("/refresh")
async def refresh(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user)
):
    """Genera un nuevo access token usando el refresh token."""
    try:
        # El refresh token viene en las cookies
        # Aquí solo renovamos el access token
        result = auth_service.token_service.create_access_token(current_user.id)
        
        response = JSONResponse(content={
            "access_token": result,
            "token_type": "bearer"
        })
        
        response.set_cookie(
            key="access_token",
            value=result,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo renovar el token"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Invalida la sesión eliminando las cookies."""
    response = JSONResponse(content={"message": "Sesión cerrada"})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response

@router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verifica la cuenta del usuario mediante el token de verificación."""
    try:
        result = auth_service.verify_email(token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
```

---

## Dependencias — Inyección en FastAPI

### dependencies.py

Define las funciones factory que FastAPI usa para inyectar dependencias.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.database.connection import get_session
from src.auth.repositories.user_repository import UserRepository
from src.auth.services.token_service import TokenService
from src.auth.services.password_service import PasswordService
from src.auth.services.email_service import EmailService
from src.auth.services.auth_service import AuthService
from src.auth.models.user import User
from src.exceptions.auth_exceptions import InvalidTokenError

# Esquema de seguridad HTTP Bearer
security = HTTPBearer()

def get_settings() -> Settings:
    """Proporciona la instancia de configuración."""
    return Settings()

def get_user_repository(
    session: Session = Depends(get_session)
) -> UserRepository:
    """Crea el repositorio de usuarios."""
    return UserRepository(session)

def get_token_service(
    settings: Settings = Depends(get_settings)
) -> TokenService:
    """Crea el servicio de tokens."""
    return TokenService(settings)

def get_password_service() -> PasswordService:
    """Crea el servicio de contraseñas."""
    return PasswordService()

def get_email_service(
    settings: Settings = Depends(get_settings)
) -> EmailService:
    """Crea el servicio de email."""
    return EmailService(settings)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
    password_service: PasswordService = Depends(get_password_service),
    email_service: EmailService = Depends(get_email_service)
) -> AuthService:
    """Crea el servicio de autenticación con todas sus dependencias."""
    return AuthService(
        user_repository=user_repo,
        token_service=token_service,
        password_service=password_service,
        email_service=email_service
    )

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    token_service: TokenService = Depends(get_token_service),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Valida el token JWT y retorna el usuario autenticado.
    
    Esta función es una dependencia que se puede usar en endpoints
    protegidos para garantizar autenticación.
    """
    try:
        token = credentials.credentials
        token_data = token_service.decode_token(token)
        user_id = token_data["user_id"]
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    
    return user
```

---

## Excepciones Personalizadas

### `src/exceptions/auth_exceptions.py`

Define excepciones de dominio que se lanzan desde servicios y repositorios.

```python
class AuthException(Exception):
    """Excepción base para errores de autenticación."""
    pass

class InvalidCredentialsError(AuthException):
    """Se lanza cuando las credenciales son inválidas."""
    pass

class InvalidTokenError(AuthException):
    """Se lanza cuando un token es inválido o expiró."""
    pass

class UserNotFoundError(AuthException):
    """Se lanza cuando un usuario no existe."""
    pass

class UserAlreadyExistsError(AuthException):
    """Se lanza cuando se intenta registrar un email ya existente."""
    pass

class InvalidPasswordError(AuthException):
    """Se lanza cuando hay un error en el hash de contraseña."""
    pass

class EmailSendError(AuthException):
    """Se lanza cuando falla el envío de correo."""
    pass
```

---

## Endpoints Disponibles

| Método | Ruta | Autenticación | Descripción |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ Pública | Registra un nuevo usuario |
| `POST` | `/auth/login` | ❌ Pública | Autentica un usuario |
| `POST` | `/auth/refresh` | ✅ Requerida | Renueva el access token |
| `GET` | `/auth/verify-email/{token}` | ❌ Pública | Verifica la cuenta por email |
| `GET` | `/auth/profile` | ✅ Requerida | Obtiene el perfil del usuario |
| `POST` | `/auth/logout` | ✅ Requerida | Cierra la sesión |

Todas las rutas usan el prefijo `/api/v1` configurado en `API_PREFIX`.

---

## Ejemplos de Uso

### 1. Registrar un Usuario

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "SecurePass123!",
    "first_name": "Juan",
    "last_name": "Pérez"
  }'
```

**Respuesta:**
```json
{
  "user_id": 1,
  "email": "usuario@example.com",
  "message": "Usuario registrado. Revisa tu correo para verificar."
}
```

### 2. Iniciar Sesión

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "SecurePass123!"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Los tokens se guardan automáticamente en cookies HTTPOnly.

### 3. Obtener Perfil (Autenticado)

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta:**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "profile_picture_url": null,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00"
}
```

### 4. Renovar Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5. Verificar Email

```bash
curl -X GET "http://localhost:8000/api/v1/auth/verify-email/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Extensibilidad y Futuras Mejoras

La arquitectura de esta plantilla está diseñada para crecer sin requerer cambios fundamentales. Aquí hay algunas extensiones que puedes agregar fácilmente:

### Docker & Containerización

Crear `Dockerfile` y `docker-compose.yml` para desarrollo y producción:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic ./alembic

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

### Testing con Pytest

```python
# tests/test_auth_service.py
import pytest
from src.auth.services.auth_service import AuthService
from src.auth.services.password_service import PasswordService

@pytest.fixture
def password_service():
    return PasswordService()

def test_password_hashing(password_service):
    plain = "SecurePass123!"
    hashed = password_service.hash_password(plain)
    assert password_service.verify_password(plain, hashed) is True
    assert password_service.verify_password("WrongPass", hashed) is False
```

### OAuth2 Social Login

Agregar autenticación con Google, GitHub, etc.:

```python
class OAuth2Service:
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def get_google_user(self, token: str) -> dict:
        # Verificar token con Google
        pass
    
    def create_or_update_user(self, provider: str, data: dict):
        # Crear usuario si no existe, actualizar si existe
        pass
```

### Roles y Permisos (RBAC)

```python
class User(SQLModel, table=True):
    # ... campos existentes ...
    role: str = Field(default="user")  # "user", "admin", "moderator"
    permissions: list[str] = Field(default=[])

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin requerido")
    return current_user
```

### Redis Caching

Cachear tokens, sesiones y datos frecuentes:

```python
from redis import Redis

class TokenCacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def invalidate_token(self, user_id: int):
        self.redis.set(f"invalid_token:{user_id}", True, ex=86400)
    
    def is_token_invalid(self, user_id: int) -> bool:
        return self.redis.exists(f"invalid_token:{user_id}")
```

### Celery para Tareas Asincrónicas

Enviar emails, generar reportes, etc. en background:

```python
from celery import Celery

celery_app = Celery("auth", broker="redis://localhost:6379")

@celery_app.task
def send_verification_email_task(email: str, token: str):
    email_service.send_verification_email(email, token)

# En el servicio
auth_service.register(...)
send_verification_email_task.delay(email, token)
```

### WebSockets para Notificaciones en Tiempo Real

```python
@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Procesar notificación
    except WebSocketDisconnect:
        pass
```

### GraphQL

Usar Strawberry o Graphene para exponer la API como GraphQL:

```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class User:
    id: int
    email: str
    first_name: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, user_id: int) -> User:
        # Obtener usuario
        pass

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

---

## Notas de Personalización

### Modificar el Modelo de Usuario

El archivo `src/auth/models/user.py` define el modelo base de usuario. Puedes extenderlo libremente con campos adicionales:

```python
class User(SQLModel, table=True):
    # ... campos existentes ...
    
    # Tus campos personalizados
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    country: Optional[str] = None
    profile_bio: Optional[str] = Field(default=None, max_length=500)
    is_newsletter_subscribed: bool = Field(default=True)
```

**Importante:** Después de modificar `models.py`, actualiza `schemas/user_schema.py` y crea una migración de Alembic:

```bash
alembic revision --autogenerate -m "Agregar campos personalizados a usuario"
alembic upgrade head
```

### Personalizar Validación de Contraseña

Modifica el método `validate_password_strength` en `PasswordService`:

```python
def validate_password_strength(self, password: str) -> tuple[bool, str]:
    # Tus reglas de validación personalizadas
    if len(password) < 6:  # Más flexible
        return False, "Contraseña muy corta"
    return True, ""
```

### Customizar Template de Email

Edita `src/templates/email_verification.html` con el diseño que desees. Usa variables Jinja2 para datos dinámicos:

```html
<html>
  <body>
    <h1>{{ app_name }}</h1>
    <p>Bienvenido, {{ user_name }}!</p>
    <a href="{{ verification_url }}">Verificar Cuenta</a>
  </body>
</html>
```

### Seguridad en Producción

Antes de deployer a producción:

1. **Cambiar `JWT_SECRET_KEY`** por una cadena larga y aleatoria
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Habilitar HTTPS**
   ```python
   # En settings
   secure_cookies = True  # Cookies solo por HTTPS
   ```

3. **Configurar CORS apropiadamente**
   ```python
   allowed_origins = ["https://miapp.com"]  # Solo tu dominio
   ```

4. **Usar variables de entorno secretas**
   - Nunca commitear `.env` a git
   - Usar secretos de tu plataforma (Vercel, AWS Secrets, etc.)

5. **Habilitar logging y monitoreo**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

---

## Troubleshooting

### "postgresql+psycopg not found"

Instala el driver:
```bash
pip install psycopg[binary]
```

### "Token inválido" pero la contraseña es correcta

Verifica que `JWT_SECRET_KEY` sea la misma en cliente y servidor.

### Email no se envía

1. Verifica credenciales SMTP en `.env`
2. Para Gmail, usa [contraseña de aplicación](https://support.google.com/accounts/answer/185833)
3. Habilita "Aplicaciones menos seguras" si es necesario

---

## Contribución y Licencia

### Cómo Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-feature`
3. Commit cambios: `git commit -m "Agregar mi-feature"`
4. Push: `git push origin feature/mi-feature`
5. Abre un Pull Request

### Licencia

Este proyecto es código abierto bajo licencia **MIT**. Ver archivo `LICENSE` para más detalles.

---

## Contacto y Soporte

- **Issues**: Abre un issue en GitHub para reportar bugs
- **Discussions**: Participa en discusiones para preguntas y sugerencias
- **Email**: soporte@example.com

---

## Changelog

### v1.0.0 (2026-06-17)

- ✅ Arquitectura OOP completa
- ✅ Autenticación JWT con access/refresh tokens
- ✅ Verificación por email
- ✅ Integración con Cloudinary
- ✅ Inyección de dependencias con FastAPI
- ✅ Documentación comprensiva
- ✅ Ejemplos de código
- ✅ Estructura preparada para escalabilidad

---

**Hecho con ❤️ por desarrolladores que valoran código limpio y mantenible.**