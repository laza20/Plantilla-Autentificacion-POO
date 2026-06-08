# FastAPI Authentication Boilerplate (PostgreSQL + JWT + Argon2)

Este repositorio es una **plantilla base (Boilerplate) agnóstica** para el manejo de usuarios, autenticación y seguridad en proyectos backend utilizando **FastAPI** y **PostgreSQL**. 

El objetivo principal de esta plantilla es automatizar la lógica repetitiva de registro, login y verificación, permitiendo iniciar nuevos proyectos con una arquitectura sólida y segura en cuestión de minutos.

---

## 🚀 Características Principales

* **Autenticación Segura:** Hashing de contraseñas utilizando `Argon2` (a través de `pwdlib` / `argon2-cffi`).
* **Gestión de Tokens:** Implementación de tokens JWT (`Access Tokens` y `Refresh Tokens`) para sesiones seguras y asíncronas.
* **Flujo de Verificación:** Sistema integrado para la verificación de cuentas mediante correo electrónico (`fastapi-mail`).
* **Base de Datos Relacional:** Configuración lista para **PostgreSQL** utilizando `SQLModel` / `SQLAlchemy` para el ORM y `Alembic` para el control de migraciones.
* **Arquitectura Desacoplada (Modular):** La tabla de credenciales (`auth`) está completamente aislada del dominio del negocio, facilitando la conexión con tablas secundarias de perfiles mediante llaves foráneas (`user_id`).
* **Variables de Entorno:** Configuración centralizada y tipada con `Pydantic-settings` (`.env`).

---

## 📁 Estructura del Proyecto Recomendada

```text
├── src/
│   ├── auth/                  # Módulo aislado de Autenticación
│   │   ├── models.py          # Tabla Core de credenciales (id, email, password_hash...)
│   │   ├── schemas.py         # Validaciones de entrada/salida (Pydantic)
│   │   ├── routes.py          # Endpoints (/register, /login, /verify, /refresh)
│   │   ├── service.py         # Lógica de negocio (crear usuario, buscar por email)
│   │   └── utils.py           # Funciones de hashing y manejo de JWT
│   ├── config/                # Configuraciones globales (base de datos, mail, envs)
│   ├── database/              # Conexión y sesión de la Base de Datos
│   └── main.py                # Punto de entrada de la aplicación FastAPI
├── migrations/                # Carpetas de Alembic para control de versiones DB
├── .env.example               # Plantilla de variables de entorno necesarias
├── requirements.txt           # Dependencias congeladas del proyecto
└── README.md
