# Sistema Inmobiliario

Plataforma de gestión inmobiliaria con aprobación de propiedades, chat en tiempo real cliente-asesor y panel administrativo. PWA instalable en escritorio y móvil.

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | FastAPI + PostgreSQL | 0.128 / 15+ |
| Frontend | Vue 3 + Pinia + Vite | 3.5 / 3 / 7.2 |
| Auth | JWT nativo HS256 | — |
| Real-time | WebSocket unificado `/ws` | — |
| ORM | SQLAlchemy + Alembic | — |
| PWA | Workbox + Leaflet Maps | — |

---

## Arquitectura

### Backend (Clean Architecture)

```
controllers → services → models
     ↓            ↓         ↓
  schemas      dbConfig   PostgreSQL
  (Pydantic)   (Session)
```

- **Core**: Configuración centralizada (Pydantic Settings), JWT, dependencias de autenticación por rol, rate limiting
- **Controllers**: Endpoints REST + WebSocket, validación JWT, permisos por rol
- **Services**: Lógica de negocio (registro, notificaciones, mensajería, post-venta, etc.)
- **Models**: Entidades SQLAlchemy con migraciones Alembic
- **Schemas**: DTOs con validación Pydantic

### Frontend (Vue 3 + Pinia)

```
views/[role]/ → components/[role]/ → shared/
     ↓                ↓
  stores         API clients (axios)
  (Pinia)        composables
```

Tres roles con layouts y vistas independientes: `client/`, `advisor/`, `admin/`. Estado global gestionado con Pinia. Comunicación en tiempo real mediante WebSocket unificado con `useWebSocket.js`.

---

## Requisitos

- **Python** 3.10+
- **PostgreSQL** 15+
- **Node.js** 18+
- **npm** 9+

---

## Instalación Rápida

### Backend

```bash
# 1. Clonar
git clone <repo>
cd backend

# 2. Entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env-example.txt .env
# Editar DATABASE_URL y SECRET_KEY

# 5. Base de datos (usar migraciones, NO el dump SQL)
psql -U postgres -c "CREATE DATABASE inmobiliaria_db"
alembic upgrade head

# 6. (Opcional) Cargar datos de prueba desde dump SQL
# psql -U postgres -d inmobiliaria_db -f docs/inmobiliaria_db.sql

# 7. Crear usuario admin manualmente (requerido tras migración limpia)
# python -c "from app.core.security import hash_password; print(hash_password('TU_PASSWORD_SEGURA'))"
# Insertar el hash resultante en la BD con rol admin

# 8. Servidor
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontendProyecto
npm install
cp .env.example .env   # configurar VITE_API_URL
npm run dev
```

---

## Variables de Entorno

### Backend (`.env`)

| Variable | Descripción | Defecto |
|----------|------------|---------|
| `DATABASE_URL` | Conexión PostgreSQL | `postgresql://postgres:pass@localhost:5432/inmobiliaria_db` |
| `SECRET_KEY` | Clave secreta JWT | — |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración token | `30` |
| `SMTP_HOST` | Servidor SMTP (email) | — |
| `SMTP_PORT` | Puerto SMTP | — |
| `SMTP_USER` | Usuario SMTP | — |
| `SMTP_PASSWORD` | Contraseña SMTP | — |
| `SMTP_FROM_EMAIL` | Remitente emails | — |
| `CORS_ORIGINS` | Orígenes permitidos | `["http://localhost:5173"]` |

### Frontend (`.env`)

| Variable | Descripción | Defecto |
|----------|------------|---------|
| `VITE_API_URL` | URL del backend | `http://localhost:8000` |

---

## Scripts Útiles

| Comando | Descripción |
|---------|------------|
| `uvicorn app.main:app --reload` | Iniciar backend (dev) |
| `alembic upgrade head` | Aplicar migraciones |
| `alembic revision --autogenerate -m "msg"` | Generar migración |
| `npm run dev` | Iniciar frontend (dev) |
| `npm run build` | Build producción |
| `npm run preview` | Vista previa build |

---

## Endpoints Principales

| Módulo | Endpoint | Descripción |
|--------|----------|-------------|
| Auth | `POST /auth/login` | Inicio de sesión |
| Auth | `POST /auth/register/*` | Registro (client/advisor) |
| Auth | `POST /auth/verify-email/{token}` | Verificar email |
| Auth | `POST /auth/forgot-password` | Solicitar cambio de contraseña |
| Auth | `POST /auth/reset-password` | Cambiar contraseña con token |
| Properties | `GET /properties` | Listar propiedades |
| Properties | `POST /properties` | Crear propiedad |
| Properties | `PUT /properties/{id}/status` | Aprobar/rechazar |
| Appointments | `GET /appointments` | Listar citas |
| Appointments | `POST /appointments` | Agendar cita |
| Messages | `GET /messages` | Obtener mensajes |
| Notifications | `GET /notifications` | Listar notificaciones |
| Notifications | `GET /notifications/meta` | Metadata de notificaciones |
| Constants | `GET /constants` | Enums del sistema |
| Health | `GET /health` | Health check |
| WebSocket | `ws://.../ws?token=JWT` | Conexión unificada |

Documentación interactiva: `http://localhost:8000/docs`

---

## Desarrollo

### Convenciones

- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/)
- **Backend**: Ruff para linting y formateo
- **Frontend**: ESLint + Prettier (según configuración del proyecto)

### Estructura del Proyecto

```text
Pagina-Web-Inmobiliaria/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # Entry point, CORS, WebSocket unificado /ws
│   │   │
│   │   ├── core/                        # Configuración central y seguridad
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Settings centralizados (Pydantic)
│   │   │   ├── security.py              # JWT encode/decode, password hashing, email tokens
│   │   │   ├── dependencies.py          # Auth dependencies (get_current_user, require_role, etc.)
│   │   │   ├── websocket.py             # ConnectionManager (singleton)
│   │   │   └── rateLimiter.py           # SlowAPI rate limiting
│   │   │
│   │   ├── models/                      # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── userModel.py             # User + is_email_verified + user_preferences (JSON)
│   │   │   ├── roleModel.py             # Role (admin, advisor, client)
│   │   │   ├── propertyModel.py         # Property
│   │   │   ├── propertyImageModel.py    # PropertyImage
│   │   │   ├── advisorModel.py          # Advisor
│   │   │   ├── appointmentModel.py      # Appointment
│   │   │   ├── favoriteModel.py         # Favorite
│   │   │   ├── conversationModel.py     # Conversation (chat)
│   │   │   ├── messageModel.py          # Message
│   │   │   ├── notificationModel.py     # Notification
│   │   │   ├── postSaleFollowupModel.py # PostSaleFollowup
│   │   │   ├── clientAdvisorModel.py    # ClientAdvisorAssignment
│   │   │   ├── activityLogModel.py      # ActivityLog
│   │   │   └── contactInquiryModel.py   # ContactInquiry
│   │   │
│   │   ├── schemas/                     # Pydantic DTOs
│   │   │   ├── __init__.py
│   │   │   ├── authSchema.py
│   │   │   ├── userSchema.py
│   │   │   ├── propertySchema.py        # PropertyTypeEnum, TransactionTypeEnum, PropertyStatusEnum
│   │   │   ├── advisorSchema.py
│   │   │   ├── appointmentSchema.py     # AppointmentStatusEnum, AppointmentTypeEnum
│   │   │   ├── favoriteSchema.py
│   │   │   ├── notificationSchema.py    # NOTIFICATION_TYPES (fuente de verdad para frontend)
│   │   │   ├── messageSchema.py
│   │   │   ├── postSaleSchema.py        # FollowupTypeEnum, FollowupStatusEnum
│   │   │   ├── clientAdvisorSchema.py
│   │   │   ├── activityLogSchema.py
│   │   │   └── contactSchema.py
│   │   │
│   │   ├── services/                    # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   ├── authService.py           # Login, register, email verification, reset password
│   │   │   ├── userService.py
│   │   │   ├── propertyService.py
│   │   │   ├── advisorService.py
│   │   │   ├── appointmentService.py
│   │   │   ├── favoriteService.py
│   │   │   ├── messageService.py        # Envío + broadcast por WebSocket
│   │   │   ├── notificationService.py   # Creación + push por WebSocket
│   │   │   ├── notificationPreferenceService.py
│   │   │   ├── postSaleService.py
│   │   │   ├── clientAdvisorService.py
│   │   │   ├── activityLogService.py    # Decorator @log_activity
│   │   │   └── contactService.py
│   │   │
│   │   ├── controllers/                 # FastAPI routers
│   │   │   ├── __init__.py
│   │   │   ├── authController.py        # /auth/* — login, register, email, reset password
│   │   │   ├── userController.py        # /users/*
│   │   │   ├── propertyController.py    # /properties/*
│   │   │   ├── advisorController.py     # /advisors/*
│   │   │   ├── appointmentController.py # /appointments/*
│   │   │   ├── favoriteController.py    # /favorites/*
│   │   │   ├── messageController.py     # /messages/* + broadcast WebSocket
│   │   │   ├── notificationController.py
│   │   │   ├── notificationPreferenceController.py
│   │   │   ├── postSaleController.py
│   │   │   ├── clientAdvisorController.py
│   │   │   ├── activityLogController.py
│   │   │   ├── contactController.py
│   │   │   └── constantsController.py   # GET /constants — enums del sistema
│   │   │
│   │   └── dbConfig/
│   │       ├── __init__.py
│   │       ├── baseModels.py            # Declarative base
│   │       └── databaseSession.py       # Engine, SessionLocal, get_db()
│   │
│   ├── alembic/                         # Migraciones (11 revisiones)
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── docs/
│   │   └── inmobiliaria_db.sql          # Schema completo v1.8.0 con seed data
│   │
│   ├── media/
│   │   ├── properties/
│   │   └── propertyImages/
│   │
│   ├── .env                             # Variables de entorno (NO subir)
│   ├── .env-example.txt
│   ├── .gitignore
│   └── requirements.txt
│
├── frontendProyecto/
│   ├── public/                          # PWA manifest, icons, service worker
│   ├── src/
│   │   ├── views/                       # Vistas de la aplicación
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── PropertiesView.vue
│   │   │   ├── PropertyDetailView.vue
│   │   │   ├── VerificadoView.vue
│   │   │   ├── RecuperarContrasenaView.vue
│   │   │   ├── NuevaContrasenaView.vue
│   │   │   ├── admin/                   # Panel admin
│   │   │   │   ├── AdminLayout.vue
│   │   │   │   ├── DashboardView.vue
│   │   │   │   ├── UsersView.vue
│   │   │   │   └── PropertiesAdminView.vue
│   │   │   ├── advisor/                 # Panel asesor
│   │   │   │   ├── AdvisorLayout.vue
│   │   │   │   ├── AdvisorDashboard.vue
│   │   │   │   ├── AdvisorPanel.vue
│   │   │   │   ├── AdvisorClientsView.vue
│   │   │   │   ├── AdvisorAppointmentsView.vue
│   │   │   │   ├── AdvisorChatView.vue
│   │   │   │   ├── AdvisorNotificationsView.vue
│   │   │   │   ├── AdvisorProfileView.vue
│   │   │   │   ├── AdvisorPostSaleView.vue
│   │   │   │   └── PropertyTable.vue
│   │   │   └── client/                  # Panel cliente
│   │   │       ├── ClientLayout.vue
│   │   │       ├── ClientDashboard.vue
│   │   │       ├── MyPropertiesView.vue
│   │   │       ├── CreatePropertyView.vue
│   │   │       ├── FavoritesView.vue
│   │   │       ├── AppointmentsView.vue
│   │   │       ├── ClientChatView.vue
│   │   │       ├── NotificationsView.vue
│   │   │       ├── ProfileView.vue
│   │   │       ├── PostSaleView.vue
│   │   │       ├── NosotrosView.vue
│   │   │       ├── ContactosView.vue
│   │   │       └── ServicesView.vue
│   │   │
│   │   ├── components/                 # Componentes reutilizables
│   │   │   ├── PropertyCard.vue
│   │   │   ├── ChatBubble.vue
│   │   │   ├── ConversationItem.vue
│   │   │   ├── TypingIndicator.vue
│   │   │   ├── AppIcon.vue
│   │   │   ├── admin/
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── Breadcrumb.vue
│   │   │   ├── advisor/
│   │   │   │   └── Sidebar.vue
│   │   │   ├── client/
│   │   │   │   └── Sidebar.vue
│   │   │   ├── properties/
│   │   │   │   └── FiltersBar.vue
│   │   │   ├── home/
│   │   │   │   ├── Hero.vue
│   │   │   │   └── FeaturedProperties.vue
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.vue
│   │   │   │   └── Footer.vue
│   │   │   └── shared/
│   │   │       ├── dashboard/
│   │   │       │   ├── DashboardHeader.vue
│   │   │       │   ├── MetricCards.vue
│   │   │       │   ├── RecentList.vue
│   │   │       │   ├── SidebarPanel.vue
│   │   │       │   ├── ActivityFeed.vue
│   │   │       │   └── StatusChart.vue
│   │   │       ├── NotificationBell.vue
│   │   │       └── ToastContainer.vue
│   │   │
│   │   ├── api/                         # Clientes Axios por módulo
│   │   │   ├── axios.js                 # Interceptor JWT + manejo 401
│   │   │   ├── auth.js
│   │   │   ├── users.js
│   │   │   ├── properties.js
│   │   │   ├── advisors.js
│   │   │   ├── appointments.js
│   │   │   ├── favorites.js
│   │   │   ├── messages.js
│   │   │   ├── notifications.js
│   │   │   └── postSale.js
│   │   │
│   │   ├── stores/                      # Pinia stores
│   │   │   ├── authStore.js
│   │   │   ├── propertyStore.js
│   │   │   ├── favoritesStore.js
│   │   │   ├── messagesStore.js
│   │   │   ├── notificationsStore.js
│   │   │   └── appointmentsStore.js
│   │   │
│   │   ├── composables/                 # Composición reutilizable
│   │   │   ├── useWebSocket.js          # WebSocket unificado (onMessage, onNotification, onTyping)
│   │   │   └── useToast.js              # Sistema de notificaciones toast
│   │   │
│   │   ├── utils/                       # Utilidades helper
│   │   │   ├── enums.js                 # Enums cargados desde GET /constants
│   │   │   ├── notificationSound.js
│   │   │   ├── chatUtils.js
│   │   │   ├── titleFormatter.js
│   │   │   └── propertyImages.js
│   │   │
│   │   ├── constants/
│   │   │   └── notifications.js         # Metadata de tipos (cargada desde API)
│   │   │
│   │   ├── router/
│   │   │   └── index.js                 # Rutas + guard beforeEach con JWT
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
```

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.
