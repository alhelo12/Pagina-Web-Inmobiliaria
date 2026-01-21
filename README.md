\# Sistema Inmobiliario Pro (MVC \& Geolocalización)



Solución integral para la gestión de bienes raíces que permite registrar propiedades, visualizar ubicaciones en mapas interactivos y gestionar flujos de aprobación por roles.



---



\## Arquitectura de Software



El proyecto utiliza una \*\*Arquitectura Multicapa (Clean Architecture)\*\* para separar las responsabilidades y facilitar el mantenimiento.



\### Backend (FastAPI + PostgreSQL)

\- \*\*Controllers\*\*: Manejan las peticiones HTTP y validan los roles de usuario.

\- \*\*Services\*\*: Contienen la lógica de negocio y las reglas de validación.

\- \*\*Models\*\*: Definen las entidades de la base de datos mediante SQLAlchemy.

\- \*\*Schemas (DTOs)\*\*: Definen la estructura de los datos que viajan entre cliente y servidor (Pydantic).

\- \*\*dbConfig\*\*: Centraliza la conexión y el ciclo de vida de las sesiones con PostgreSQL.



\### Frontend (Vue.js 3 + Pinia + Vite)

\- \*\*Vite\*\*: Motor de construcción de alta velocidad para desarrollo y producción.

\- \*\*Pinia\*\*: Almacén central (Store) para gestionar el estado global (JWT, roles, datos del mapa).

\- \*\*Views\*\*: Interfaces reactivas divididas por el rol del usuario (Admin, Asesor, Cliente).



---



/Pagina-Web-Inmobiliaria

│

├──  backendProyecto (FastAPI + PostgreSQL)

│   ├──  app

│   │   ├──  dbConfig/           # CONEXIÓN Y CONFIGURACIÓN DE DB

│   │   │   ├── databaseSession.py # Engine y SessionLocal (PostgreSQL)

│   │   │   └── baseModels.py      # Unión para modelos y migraciones

│   │   │

│   │   ├──  controllers/        # RUTAS DIVIDIDAS POR ROL

│   │   │   ├── authController.py  # Login y Registro

│   │   │   ├── adminController.py # Gestión de usuarios y asesores

│   │   │   ├── advisorController.py # Revisión y aprobación de casas

│   │   │   └── clientController.py  # Carga de propiedades y "Mis Casas"

│   │   │

│   │   ├──  services/           # LÓGICA DE NEGOCIO POR ROL

│   │   │   ├── adminService.py

│   │   │   ├── advisorService.py

│   │   │   └── clientService.py

│   │   │

│   │   ├──  models/             # MODELOS DE DATOS (SQLAlchemy)

│   │   │   ├── userModel.py       # Roles: Admin, Asesor, Cliente

│   │   │   ├── propertyModel.py   # Datos de la casa y coordenadas

│   │   │   └── imageModel.py      # Registro de URLs de imágenes

│   │   │

│   │   ├──  schemas/            # Validaciones Pydantic (DTOs)

│   │   ├──  core/               # Seguridad JWT (Secret Key, Hashing)

│   │   └── main.py                # Punto de entrada de la API

│   │

│   ├──  media/                  # ALMACENAMIENTO DE IMÁGENES (.jpg, .png)

│   │   └──  propertyImages/     # Fotos subidas por los clientes

│   │

│   ├──  dbMigrations/           # Historial de cambios en DB (Alembic)

│   ├── .env                       # VARIABLES DE ENTORNO

│   └── requirements.txt           # Dependencias de Python

│

├──  frontendProyecto (Vue.js + Vite)

│   ├──  src

│   │   ├──  views/              # Vistas de Admin, Advisor y Client

│   │   ├──  components/         # Mapas (Leaflet), Cards y UI

│   │   ├──  apiServices/        # Clientes Axios por cada controlador

│   │   └──  store/              # Pinia: Auth, Roles y Propiedades

│   └── package.json

│

├── .gitignore                     

└── README.md

