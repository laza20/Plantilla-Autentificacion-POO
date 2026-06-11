# 🔐 FastAPI Authentication Boilerplate

> **PostgreSQL · JWT · Argon2 · Cloudinary · FastAPI-Mail**

Una **plantilla base (Boilerplate) agnóstica** para el manejo de usuarios, autenticación y seguridad en proyectos backend con **FastAPI** y **PostgreSQL**. Diseñada para eliminar la lógica repetitiva de registro, login y verificación, permitiendo iniciar nuevos proyectos con una arquitectura sólida y segura en cuestión de minutos.

---

## 📋 Tabla de Contenido

- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Variables de Entorno (.env)](#-variables-de-entorno-env)
- [Descripción de Módulos](#-descripción-de-módulos)
- [Endpoints Disponibles](#-endpoints-disponibles)
- [Notas de Uso y Personalización](#-notas-de-uso-y-personalización)

---

## 🚀 Características Principales

| Característica | Descripción |
|---|---|
| 🔒 **Hashing Seguro** | Contraseñas encriptadas con `Argon2` vía `pwdlib` / `argon2-cffi` |
| 🎟️ **Tokens JWT** | `Access Token` de corta duración + `Refresh Token` de larga duración, almacenados en cookies |
| ✉️ **Verificación por Mail** | Flujo completo de verificación de cuenta mediante correo electrónico (`fastapi-mail`) |
| 🗄️ **PostgreSQL + ORM** | Configuración lista para PostgreSQL con `SQLModel` / `SQLAlchemy` y migraciones via `Alembic` |
| 🖼️ **Gestión de Imágenes** | Integración con **Cloudinary** para carga y almacenamiento de imágenes de perfil |
| 🧩 **Arquitectura Modular** | Tabla de credenciales desacoplada del dominio del negocio; conectable a perfiles vía `user_id` |
| ⚙️ **Configuración Centralizada** | Variables de entorno tipadas y validadas con `Pydantic-settings` |
| 🛡️ **Validación de Contraseña** | Función de verificación de estándares de seguridad (configurable) |

---

## 🛠️ Tecnologías Utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/)** — Framework web asíncrono de alto rendimiento
- **[SQLModel](https://sqlmodel.tiangolo.com/) / [SQLAlchemy](https://www.sqlalchemy.org/)** — ORM para interacción con la base de datos
- **[Alembic](https://alembic.sqlalchemy.org/)** — Control de migraciones de base de datos
- **[PostgreSQL](https://www.postgresql.org/)** — Motor de base de datos relacional
- **[Argon2 / pwdlib](https://argon2-cffi.readthedocs.io/)** — Algoritmo moderno para hashing de contraseñas
- **[Python-JOSE](https://python-jose.readthedocs.io/)** — Generación y validación de tokens JWT
- **[Cloudinary](https://cloudinary.com/)** — Plataforma de gestión de imágenes en la nube
- **[FastAPI-Mail](https://sabuhish.github.io/fastapi-mail/)** — Envío de correos electrónicos
- **[Pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — Gestión de configuración por variables de entorno

---

## 📁 Estructura del Proyecto

```
auth/
├── .env                        # Variables de entorno (NO incluir en git)
├── .gitignore
├── requirements.txt
├── README.md
├── venv/                       # Entorno virtual (recomendado, no en git)
└── src/
    ├── main.py                 # Punto de entrada de la aplicación
    ├── config/
    │   └── config.py           # Modelo de configuración global (settings)
    ├── templates/
    │   └── verificacion.html   # Plantilla HTML para el correo de verificación
    ├── utils/
    │   └── mail_utils.py       # Lógica de configuración y envío de correos
    ├── cloudinary/
    │   └── cloudinary_utils.py # Lógica de carga de imágenes a Cloudinary
    └── auth/
        ├── models.py           # Modelos de base de datos del usuario (modificable)
        ├── repository.py       # Lógica de acceso a datos (queries / operaciones)
        ├── routers.py          # Definición de endpoints de autenticación
        ├── transformers.py     # Transformadores/schemas de entrada (Pydantic)
        ├── dependencies/
        │   └── dependencies.py # Dependencias de FastAPI (verificación de sesión activa)
        ├── security/
        │   └── security.py      # Funciones de hash y verificación de contraseña, encode y decode token.
        │   
        ├── tokens/
        │   └── tokens.py       # Creación de access_token, refresh_token y refresco
        └── utils/
            └── usuarios_utils.py # Verificación de usuario y validación de contraseña
```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd auth
```

### 2. Crear y activar el entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux / macOS)
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crear un archivo `.env` en la raíz del proyecto con el contenido indicado en la sección [Variables de Entorno](#-variables-de-entorno-env).

### 5. Ejecutar la aplicación

```bash
uvicorn src.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

La documentación interactiva (Swagger UI) en: `http://localhost:8000/docs`

---

## 🔑 Variables de Entorno (.env)

A continuación se detalla cada variable requerida y su propósito.

### Base de Datos

```env
# Cadena de conexión para PostgreSQL (via psycopg)
# Formato: postgresql+psycopg://usuario:contraseña@host:puerto/nombre_base
DATABASE_URL="postgresql+psycopg://postgres:123456@localhost:5432/mi_base"
```

### Cloudinary

```env
CLOUDINARY_CLOUD_NAME="mi_cloud"           # Nombre de tu cuenta en Cloudinary
CLOUDINARY_API_KEY="123456789012345"        # Clave pública de la API
CLOUDINARY_API_SECRET="abc123xyz456"        # Clave privada de la API
CLOUDINARY_UPLOAD_PRESET="usuarios"         # Carpeta/preset donde se almacenan las imágenes
```

### JWT — Autenticación

```env
JWT_SECRET_KEY="MiClaveSuperSecreta123456789"  # Clave secreta para firmar tokens (usar una llave larga y compleja)
ALGORITHM="HS256"                              # Algoritmo de firma
ACCESS_TOKEN_EXPIRE_MINUTES=30                 # Duración del access token en minutos (ej: 30 = media hora)
REFRESH_TOKEN_DURATION=7                       # Duración del refresh token en días (ej: 7 = una semana)
```

### Correo Electrónico

```env
MAIL_USERNAME="miapp@gmail.com"        # Correo remitente
MAIL_PASSWORD="abcd efgh ijkl mnop"   # Contraseña de aplicación (no la contraseña principal)
MAIL_FROM="miapp@gmail.com"           # Dirección que aparece como remitente
MAIL_PORT=587                          # Puerto SMTP (587 para TLS, 465 para SSL)
MAIL_SERVER="smtp.gmail.com"          # Servidor SMTP (smtp.gmail.com / smtp.office365.com)
MAIL_STARTTLS=True                    # Habilitar TLS (recomendado para Gmail)
MAIL_SSL_TLS=False                    # Habilitar SSL directo
USE_CREDENTIALS=True                  # Usar credenciales para autenticarse
```

> 💡 **Gmail:** Se recomienda usar una [contraseña de aplicación](https://support.google.com/accounts/answer/185833) en lugar de la contraseña principal de la cuenta.

### Configuración de la Aplicación

```env
BASE_URL="http://localhost:8000"       # URL base donde corre la API
NOMBRE_APP="PRUEBA-PLANTILLA"         # Prefijo para todas las rutas de la API
```

> Las rutas generadas serán del estilo:
> `http://localhost:8000/PRUEBA-PLANTILLA/usuarios/login`

---

### Ejemplo Completo de `.env`

```env
# =========================
# Base de Datos PostgreSQL
# =========================
DATABASE_URL="postgresql+psycopg://postgres:123456@localhost:5432/mi_base"

# =========================
# Cloudinary
# =========================
CLOUDINARY_CLOUD_NAME="mi_cloud"
CLOUDINARY_API_KEY="123456789012345"
CLOUDINARY_API_SECRET="abc123xyz456"
CLOUDINARY_UPLOAD_PRESET="usuarios"

# =========================
# JWT
# =========================
JWT_SECRET_KEY="MiClaveSuperSecreta123456789"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_DURATION=7

# =========================
# Correo Electrónico
# =========================
MAIL_USERNAME="miapp@gmail.com"
MAIL_PASSWORD="abcd efgh ijkl mnop"
MAIL_FROM="miapp@gmail.com"
MAIL_PORT=587
MAIL_SERVER="smtp.gmail.com"
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True

# =========================
# Aplicación
# =========================
BASE_URL="http://localhost:8000"
NOMBRE_APP="PRUEBA-PLANTILLA"
```

---

## 📦 Descripción de Módulos

### `src/main.py`
Punto de entrada principal de la aplicación. Configura la instancia de FastAPI, registra los routers y establece los middlewares necesarios.

---

### `src/config/config.py` — `settings`
Modelo de configuración centralizado basado en `Pydantic-settings`. Lee y valida automáticamente todas las variables del archivo `.env`. Accesible en toda la aplicación como `settings`.

---

### `src/auth/models.py`
Define el modelo de base de datos del usuario usando `SQLModel`. Este archivo **puede y debe modificarse** según las necesidades particulares de cada proyecto (agregar campos, relaciones, etc.).

---

### `src/auth/transformers.py`
Contiene los schemas `Pydantic` utilizados para la recepción y validación de datos en los endpoints (ej.: datos de registro, login, actualización de perfil). Si se modifica `models.py`, este archivo también debe actualizarse para reflejar los cambios, especialmente en lo que respecta al manejo de imágenes.

---

### `src/auth/repository.py`
Contiene toda la lógica de acceso a datos: consultas, creación, actualización y eliminación de registros. Actúa como la capa de persistencia del sistema de autenticación.

---

### `src/auth/routers.py`
Define los endpoints HTTP del sistema de autenticación (registro, login, logout, verificación, refresco de token, etc.). Utiliza las dependencias y el repositorio para orquestar cada operación.

---

### `src/auth/dependencies/dependencies.py`
Dependencias de FastAPI que se inyectan en los endpoints protegidos. Verifican que el usuario cuente con un `access_token` válido en sus cookies antes de permitir el acceso al recurso.

---

### `src/auth/security/`
Contiene dos archivos de seguridad críticos:
- **`hashing.py`**: Funciones para hashear y verificar contraseñas usando `Argon2`.
- **`jwt_handler.py`**: Funciones para codificar y decodificar tokens JWT usando la clave secreta y el algoritmo configurados.

---

### `src/auth/tokens/tokens.py`
Gestiona la creación del `access_token`, el `refresh_token` y la lógica de refresco de sesión. El `refresh_token` permite extender la sesión del usuario sin necesidad de que vuelva a ingresar sus credenciales.

---

### `src/auth/utils/usuarios_utils.py`
Contiene funciones auxiliares del dominio de usuarios:
- **Verificación de usuario**: Comprueba la existencia y estado del usuario en la base de datos.
- **Validación de contraseña**: Verifica que la contraseña cumpla con estándares mínimos de seguridad (longitud, mayúsculas, caracteres especiales, etc.). Los parámetros son completamente configurables según las necesidades del proyecto.

---

### `src/cloudinary/`
Encapsula la lógica de interacción con la API de Cloudinary: carga de imágenes, obtención de URLs públicas y manejo de errores. Se invoca desde el repositorio o los routers al procesar imágenes de perfil.

---

### `src/utils/mail_utils.py`
Configura la instancia de `FastAPI-Mail` con las credenciales del `.env` y provee la función encargada de armar y despachar el correo de verificación de cuenta.

---

### `src/templates/verificacion.html`
Plantilla HTML del correo de verificación. Puede modificarse libremente para adaptarla al branding de cada proyecto. Requiere dos valores dinámicos:

| Variable | Descripción |
|---|---|
| `NOMBRE_APP` | Nombre de la aplicación (se inyecta desde la variable de entorno) |
| `url_verificacion` | URL completa al endpoint de verificación de cuenta |

---

## 🌐 Endpoints Disponibles

Las rutas se generan automáticamente con el prefijo definido en `NOMBRE_APP`. Ejemplo con `NOMBRE_APP="PRUEBA-PLANTILLA"`:

| Método | Ruta | Descripción | Autenticación |
|---|---|---|---|
| `POST` | `/PRUEBA-PLANTILLA/usuarios/registrar` | Registra un nuevo usuario y envía email de verificación | ❌ Pública |
| `GET` | `/PRUEBA-PLANTILLA/usuarios/verificar/{token}` | Verifica la cuenta del usuario mediante el token recibido por mail | ❌ Pública |
| `POST` | `/PRUEBA-PLANTILLA/usuarios/login` | Autentica al usuario y devuelve `access_token` y `refresh_token` en cookies | ❌ Pública |
| `POST` | `/PRUEBA-PLANTILLA/usuarios/logout` | Invalida la sesión eliminando las cookies de autenticación | ✅ Requerida |
| `POST` | `/PRUEBA-PLANTILLA/usuarios/refresh` | Renueva el `access_token` usando el `refresh_token` almacenado en cookie | ✅ Requerida |
| `GET` | `/PRUEBA-PLANTILLA/usuarios/perfil` | Retorna los datos del usuario autenticado | ✅ Requerida |
| `PUT` | `/PRUEBA-PLANTILLA/usuarios/actualizar` | Actualiza los datos del perfil del usuario | ✅ Requerida |

> La documentación interactiva completa está disponible en `/docs` (Swagger UI) y `/redoc` (ReDoc) una vez iniciada la aplicación.

---

## 📝 Notas de Uso y Personalización

**Modelo de usuario:** El archivo `src/auth/models.py` define un modelo base pensado como punto de partida. Se recomienda extenderlo con los campos que requiera el proyecto (nombre completo, rol, teléfono, etc.). Ante cualquier cambio en el modelo, actualizar también `transformers.py`.

**Validación de contraseña:** La función en `src/auth/utils/usuarios_utils.py` aplica reglas básicas de seguridad. Los parámetros (longitud mínima, requerimiento de mayúsculas, números, caracteres especiales) son ajustables según la política de seguridad del proyecto.

**Template de correo:** El archivo `src/templates/verificacion.html` puede personalizarse con el diseño que se desee. Solo asegurarse de mantener la inyección del `NOMBRE_APP` y la `url_verificacion`.

**Arquitectura desacoplada:** El sistema de autenticación está completamente aislado del dominio del negocio. Para asociar datos de perfil extendidos, se recomienda crear una tabla separada (ej.: `Perfil`) con una llave foránea apuntando al `user_id` de la tabla de autenticación.

**Seguridad en producción:**
- Cambiar `JWT_SECRET_KEY` por una cadena larga, aleatoria y única.
- Configurar `BASE_URL` con el dominio real de producción.
- Asegurarse de que las cookies se sirvan sobre HTTPS (configurar `secure=True` en los cookies de producción).
- No incluir el archivo `.env` en el repositorio (ya incluido en `.gitignore`).

---

## 📄 Licencia

Este proyecto es una plantilla de uso libre. Modificar y adaptar según las necesidades de cada proyecto.
