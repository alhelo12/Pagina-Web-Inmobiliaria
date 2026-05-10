# Sistema Inmobiliario Hibrido (PWA y Geolocalizacion)

Solucion integral para la gestion de bienes raices. Plataforma disenada como una PWA (Progressive Web App) optimizada para navegadores de escritorio y dispositivos moviles.

---

## Arquitectura de Software

El proyecto utiliza una Arquitectura Multicapa (Clean Architecture) para separar responsabilidades y facilitar el escalamiento.

### Backend (FastAPI + PostgreSQL)
- **Core**: Configuración centralizada, seguridad JWT y dependencias de autenticación.
- **Controllers**: Manejan las peticiones HTTP, validan JWT y verifican permisos por rol.
- **Services**: Contienen la logica de negocio y las reglas de validacion (84 funciones).
- **Models**: Definen las entidades de la base de datos mediante SQLAlchemy (7 modelos).
- **Schemas (DTOs)**: Definen la estructura de los datos con Pydantic (59 schemas).
- **dbConfig**: Centraliza la conexion, connection pooling y el ciclo de vida de las sesiones.

### Sistema de Autenticación
- **JWT Tokens**: Autenticación mediante tokens Bearer con expiración de 30 minutos.
- **Roles**: Admin (1), Advisor (2), Client (3) con permisos específicos.
- **Protección de Endpoints**: 48 de 72 endpoints requieren autenticación.
- **Validación de Ownership**: Usuarios solo pueden modificar sus propios recursos.

### Frontend Hibrido (Vue.js 3 + Pinia + Vite)
- **PWA**: Configuracion para instalacion en pantalla de inicio de dispositivos moviles.
- **Leaflet Maps**: Visualizacion interactiva de propiedades mediante coordenadas.
- **Pinia**: Gestion de estado global (Sesion, Roles y Propiedades).
- **Responsive Design**: Interfaz adaptada a multiples resoluciones.

---

## Estructura del Proyecto

```text
/Pagina-Web-Inmobiliaria
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # Entry point, CORS, startup events
│   │   │
│   │   ├── core/                        # Configuración central y seguridad
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Settings centralizados (Pydantic)
│   │   │   ├── security.py              # JWT encode/decode, password hashing
│   │   │   └── dependencies.py          # Auth dependencies (get_current_user, require_admin, etc.)
│   │   │
│   │   ├── models/                      # SQLAlchemy ORM models (7 modelos)
│   │   │   ├── __init__.py
│   │   │   ├── userModel.py             # User, Role
│   │   │   ├── roleModel.py             # Role
│   │   │   ├── propertyModel.py        # Property
│   │   │   ├── propertyImageModel.py    # PropertyImage
│   │   │   ├── advisorModel.py         # Advisor
│   │   │   ├── appointmentModel.py     # Appointment
│   │   │   └── favoriteModel.py        # Favorite
│   │   │
│   │   ├── schemas/                     # Pydantic schemas - DTOs (59 schemas)
│   │   │   ├── __init__.py
│   │   │   ├── authSchema.py            # Token, PasswordChange (4 schemas)
│   │   │   ├── userSchema.py            # UserCreate, UserResponse, ClientRegister, etc. (18 schemas)
│   │   │   ├── propertySchema.py        # PropertyCreate, PropertySearch, NearbySearch, etc. (15 schemas)
│   │   │   ├── advisorSchema.py         # AdvisorCreate, AdvisorStats, etc. (8 schemas)
│   │   │   ├── appointmentSchema.py     # AppointmentCreate, AppointmentUpdate, etc. (8 schemas)
│   │   │   └── favoriteSchema.py        # FavoriteResponse, FavoriteToggle, etc. (6 schemas)
│   │   │
│   │   ├── services/                    # Business logic layer (6 services, 84 funciones)
│   │   │   ├── __init__.py
│   │   │   ├── authService.py           # Login, register, password validation (8 funciones)
│   │   │   ├── userService.py           # User CRUD, activate/deactivate (14 funciones)
│   │   │   ├── propertyService.py       # Property CRUD, search, approve/reject (18 funciones)
│   │   │   ├── advisorService.py        # Advisor CRUD, stats, rating (15 funciones)
│   │   │   ├── appointmentService.py    # Appointment management, confirm/complete (14 funciones)
│   │   │   └── favoriteService.py       # Favorites toggle, check multiple (15 funciones)
│   │   │
│   │   ├── controllers/                 # API endpoints - FastAPI routers (6 controllers, 68 endpoints)
│   │   │   ├── __init__.py
│   │   │   ├── authController.py        # /auth/* - Login, register, change password (6 endpoints)
│   │   │   ├── userController.py        # /users/* - User CRUD, admin only (8 endpoints) 🔐
│   │   │   ├── propertyController.py    # /properties/* - CRUD, search, approve (18 endpoints) 🔐
│   │   │   ├── advisorController.py     # /advisors/* - Advisor info, stats (13 endpoints)
│   │   │   ├── appointmentController.py # /appointments/* - Appointment management (14 endpoints) 🔐
│   │   │   └── favoriteController.py    # /favorites/* - Toggle, check favorites (13 endpoints) 🔐
│   │   │
│   │   └── dbConfig/                    # Database configuration
│   │       ├── __init__.py
│   │       ├── baseModels.py            # Declarative base para SQLAlchemy
│   │       └── databaseSession.py       # Engine, SessionLocal, connection pooling, get_db()
│   │
│   ├── docs/
│   │   └── inmobiliaria_db.sql          # Complete DB schema con triggers y seed data
│   │
│   ├── media/
│   │   ├── properties/                  # Imagenes de propiedades subidas
│   │   └── propertyImages/               # Imagenes adicionales
│   │
│   ├── .env                             # Environment variables (NO subir a Git)
│   ├── .env-example.txt                 # Template de variables de entorno
│   ├── .gitignore                       # Archivos ignorados por Git
│   └── requirements.txt                 # Python dependencies
│
├── frontendProyecto/
│   ├── public/                          # Archivos estaticos y configuracion PWA
│   ├── src/
│   │   ├── views/                       # Vistas de la aplicación
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── PropertiesView.vue
│   │   │   ├── PropertyDetailView.vue
│   │   │   ├── admin/                    # Vistas de administrador
│   │   │   │   ├── AdminLayout.vue
│   │   │   │   ├── DashboardView.vue
│   │   │   │   ├── UsersView.vue
│   │   │   │   └── PropertiesAdminView.vue
│   │   │   ├── advisor/                 # Vistas de asesor
│   │   │   │   ├── AdvisorLayout.vue
│   │   │   │   ├── AdvisorDashboard.vue
│   │   │   │   ├── AdvisorPanel.vue
│   │   │   │   ├── AdvisorClientsView.vue
│   │   │   │   └── PropertyTable.vue
│   │   │   └── client/                  # Vistas de cliente
│   │   │       ├── FavoritesView.vue
│   │   │       ├── ServicesView.vue
│   │   │       ├── NosotrosView.vue
│   │   │       ├── CreatePropertyView.vue
│   │   │       └── ContactosView.vue
│   │   │
│   │   ├── components/                 # Componentes reutilizables
│   │   │   ├── PropertyCard.vue
│   │   │   ├── admin/                   # Componentes de admin
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── dashboard/
│   │   │   │       ├── AdminMetricCards.vue
│   │   │   │       ├── AdminRecentList.vue
│   │   │   │       ├── AdminRightPanel.vue
│   │   │   │       ├── AdminStatusChart.vue
│   │   │   │       └── AdminDashboardHeader.vue
│   │   │   ├── advisor/                 # Componentes de asesor
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── dashboard/
│   │   │   │       ├── AdvisorMetricCards.vue
│   │   │   │       ├── AdvisorRecentList.vue
│   │   │   │       ├── AdvisorRightPanel.vue
│   │   │   │       ├── AdvisorAvailablePanel.vue
│   │   │   │       └── AdvisorDashboardHeader.vue
│   │   │   ├── properties/              # Componentes de propiedades
│   │   │   │   └── FiltersBar.vue
│   │   │   ├── home/                    # Componentes de inicio
│   │   │   │   ├── Hero.vue
│   │   │   │   ├── SearchBar.vue
│   │   │   │   └── FeaturedProperties.vue
│   │   │   ├── layout/                  # Componentes de diseño
│   │   │   │   ├── Navbar.vue
│   │   │   │   └── Footer.vue
│   │   │   └── shared/                  # Componentes compartidos
│   │   │       └── Toast.vue
│   │   │
│   │   ├── api/                         # Clientes Axios por servicio
│   │   │   ├── axios.js
│   │   │   ├── auth.js
│   │   │   ├── users.js
│   │   │   ├── properties.js
│   │   │   ├── advisors.js
│   │   │   └── favorites.js
│   │   │
│   │   ├── stores/                      # Pinia stores
│   │   │   ├── authStore.js
│   │   │   ├── propertyStore.js
│   │   │   └── favoritesStore.js
│   │   │
│   │   ├── utils/                       # Utilidades helper
│   │   │   ├── titleFormatter.js
│   │   │   └── propertyImages.js
│   │   │
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   │
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── .gitignore
├── LICENSE
└── README.md

🔐 = Endpoints protegidos con JWT

Total Backend:
- 7 Models (SQLAlchemy ORM)
- 59 Schemas (Pydantic validation)
- 6 Services (84 funciones de lógica de negocio)
- 6 Controllers (68 endpoints REST)
- 48 endpoints protegidos con JWT
- 24 endpoints públicos
```

---

## 🚀 Instalación del Backend

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10 o superior** ([Descargar Python](https://www.python.org/downloads/))
- **PostgreSQL 15 o superior** ([Descargar PostgreSQL](https://www.postgresql.org/download/))
- **pip** (Python package manager - incluido con Python)
- **Git** ([Descargar Git](https://git-scm.com/downloads))

---

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/Pagina-Web-Inmobiliaria.git
cd Pagina-Web-Inmobiliaria/backend
```

---

### Paso 2: Crear Entorno Virtual

Es recomendable usar un entorno virtual para aislar las dependencias del proyecto:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comando, indicando que el entorno virtual está activo.

---

### Paso 3: Instalar Dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias:
- FastAPI, Uvicorn
- SQLAlchemy, psycopg2-binary
- Pydantic, pydantic-settings
- python-jose, passlib
- Y todas las demás dependencias

---

### Paso 4: Configurar PostgreSQL

#### 4.1 Crear la Base de Datos

Abre **pgAdmin** o usa la terminal `psql`:

**Opción A - Usando pgAdmin:**
1. Abrir pgAdmin
2. Click derecho en "Databases" → "Create" → "Database"
3. Nombre: `inmobiliaria_db`
4. Click "Save"

**Opción B - Usando psql (terminal):**
```bash
# Windows (PowerShell)
psql -U postgres

# Linux/Mac
sudo -u postgres psql
```

Dentro de psql:
```sql
CREATE DATABASE inmobiliaria_db;
\q
```

#### 4.2 (Opcional) Crear Usuario Específico

Si prefieres no usar el usuario `postgres`:

```sql
-- Crear usuario
CREATE USER inmobiliaria_user WITH PASSWORD 'tu_password_segura';

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE inmobiliaria_db TO inmobiliaria_user;
```

---

### Paso 5: Ejecutar el Schema SQL

Ejecuta el archivo `docs/inmobiliaria_db.sql` para crear todas las tablas, triggers y datos iniciales:

**Opción A - Usando pgAdmin:**
1. En pgAdmin, conectar a la base de datos `inmobiliaria_db`
2. Click derecho en `inmobiliaria_db` → "Query Tool"
3. Abrir el archivo `docs/inmobiliaria_db.sql`
4. Click en "Execute" (⚡)

**Opción B - Usando psql (terminal):**
```bash
# Navegar a la carpeta backend
cd backend

# Ejecutar el script (Windows/Linux/Mac)
psql -U postgres -d inmobiliaria_db -f docs/inmobiliaria_db.sql
```

Esto creará:
- ✅ 7 tablas (users, roles, properties, property_images, advisors, appointments, favorites)
- ✅ Triggers automáticos para `updated_at`
- ✅ 3 roles (admin, advisor, client)
- ✅ 1 usuario admin de prueba
- ✅ 2 asesores con propiedades de ejemplo

---

### Paso 6: Configurar Variables de Entorno

Crear un archivo `.env` en la carpeta `/backend`:

```bash
# Windows
type nul > .env

# Linux/Mac
touch .env
```

Abrir el archivo `.env` y agregar estas variables:

```env
# ==========================================
# APLICACIÓN
# ==========================================
APP_NAME=Inmobiliaria API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

# ==========================================
# BASE DE DATOS
# ==========================================
# Cambiar 'usuario' y 'password' por tus credenciales de PostgreSQL
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/inmobiliaria_db

# Pool de conexiones (opcional - usa defaults seguros si no se especifican)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=1800
DB_POOL_PRE_PING=True
DB_ECHO=False

# ==========================================
# JWT / SEGURIDAD
# ==========================================
# IMPORTANTE: Generar una clave secreta segura (ver abajo)
SECRET_KEY=desarrollo_secret_key_temporal_cambiar_en_produccion_12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==========================================
# CORS (Permitir acceso desde frontend)
# ==========================================
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=True

# ==========================================
# API (opcional - usa defaults)
# ==========================================
API_PREFIX=
DOCS_URL=/docs
REDOC_URL=/redoc

# ==========================================
# PAGINACIÓN (opcional - usa defaults)
# ==========================================
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

#### Generar SECRET_KEY Segura

Para producción, genera una clave secreta real:

**Opción 1 - Python:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Opción 2 - OpenSSL:**
```bash
openssl rand -hex 32
```

Copia el resultado y reemplaza el valor de `SECRET_KEY` en el `.env`.

---

### Paso 7: Verificar la Instalación

Con el entorno virtual activado, inicia el servidor:

```bash
uvicorn app.main:app --reload
```

Deberías ver una salida similar a:

```
================================================================================
🚀 Iniciando Inmobiliaria API...
================================================================================
--- CONEXION A BASE DE DATOS: EXITOSA ---
✅ Conexión a PostgreSQL: OK
📊 Connection Pool: 5 conexiones disponibles
================================================================================
📚 Documentación disponible en: http://localhost:8000/docs
================================================================================
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Paso 8: Probar la API

#### 8.1 Verificar que el servidor está funcionando

Abre tu navegador y ve a:
```
http://localhost:8000
```

Deberías ver:
```json
{
  "message": "Inmobiliaria API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

#### 8.2 Verificar la conexión a la base de datos

```
http://localhost:8000/health/db
```

Deberías ver:
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "type": "postgresql"
  },
  "connection_pool": {
    "pool_size": 5,
    ...
  }
}
```

#### 8.3 Abrir la documentación interactiva (Swagger)

```
http://localhost:8000/docs
```

Aquí podrás:
- Ver todos los endpoints disponibles
- Probar cada endpoint directamente
- Ver ejemplos de request/response
- Autenticarte con JWT

---

### Paso 9: Probar el Sistema de Autenticación

#### 9.1 Login con usuario admin (creado automáticamente)

En Swagger (`http://localhost:8000/docs`):

1. Buscar el endpoint `POST /auth/login`
2. Click en "Try it out"
3. En el formulario:
   - **username:** `admin@inmobiliaria.com`
   - **password:** `Admin123`
4. Click "Execute"

Deberías recibir un token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 9.2 Autenticarte en Swagger

1. Copia el `access_token` (sin las comillas)
2. Click en el botón **"Authorize"** (🔒 candado verde arriba a la derecha)
3. Pega el token en el campo "Value"
4. Click "Authorize"
5. Click "Close"

Ahora puedes probar todos los endpoints protegidos (marcados con 🔐).

#### 9.3 Probar endpoint protegido

Prueba `GET /auth/me`:
1. Buscar el endpoint en Swagger
2. Click "Try it out"
3. Click "Execute"

Deberías ver tu información de usuario:
```json
{
  "id": 1,
  "full_name": "Administrador",
  "email": "admin@inmobiliaria.com",
  "role": {
    "id": 1,
    "name": "admin"
  },
  "is_active": true
}
```

---

## 🎯 Usuarios de Prueba

El `schema.sql` crea estos usuarios automáticamente:

| Email | Password | Rol | Descripción |
|-------|----------|-----|-------------|
| admin@inmobiliaria.com | Admin123 | admin | Acceso total al sistema |
| (Crear en /auth/register/client) | - | client | Cliente normal |

**Nota:** Para crear usuarios advisor, usar `POST /auth/register` como admin y especificar `role_id: 2`.

---

## 🎉 ¡Instalación Completa!

Si llegaste hasta aquí, tu backend debería estar funcionando correctamente:

```
✅ PostgreSQL instalado y corriendo
✅ Base de datos creada con tablas y datos de prueba
✅ Entorno virtual de Python configurado
✅ Dependencias instaladas
✅ Variables de entorno configuradas
✅ Servidor corriendo en http://localhost:8000
✅ Documentación accesible en http://localhost:8000/docs
✅ Sistema de autenticación JWT funcionando
✅ Endpoints protegidos correctamente
```
