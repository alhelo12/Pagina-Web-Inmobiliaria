# Sistema Inmobiliario Hibrido (PWA y Geolocalizacion)

Solucion integral para la gestion de bienes raices. Plataforma disenada como una PWA (Progressive Web App) optimizada para navegadores de escritorio y dispositivos moviles.

---

## Arquitectura de Software

El proyecto utiliza una Arquitectura Multicapa (Clean Architecture) para separar responsabilidades y facilitar el escalamiento.

### Backend (FastAPI + PostgreSQL)
- Controllers: Manejan las peticiones HTTP y validan los roles de usuario.
- Services: Contienen la logica de negocio y las reglas de validacion.
- Models: Definen las entidades de la base de datos mediante SQLAlchemy.
- Schemas (DTOs): Definen la estructura de los datos (Pydantic).
- dbConfig: Centraliza la conexion y el ciclo de vida de las sesiones.

### Frontend Hibrido (Vue.js 3 + Pinia + Vite)
- PWA: Configuracion para instalacion en pantalla de inicio de dispositivos moviles.
- Leaflet Maps: Visualizacion interactiva de propiedades mediante coordenadas.
- Pinia: Gestion de estado global (Sesion, Roles y Propiedades).
- Responsive Design: Interfaz adaptada a multiples resoluciones.

---

## Estructura del Proyecto


```text
/Pagina-Web-Inmobiliaria
│
├── backend
│   ├── app
│   │   ├── dbConfig/           # Conexion y configuracion de DB
│   │   │   ├── databaseSession.py
│   │   │   └── baseModels.py
│   │   ├── controllers/        # Rutas divididas por rol
│   │   │   ├── authController.py
│   │   │   ├── adminController.py
│   │   │   ├── advisorController.py
│   │   │   └── clientController.py
│   │   ├── services/           # Logica de negocio por rol
│   │   ├── models/             # Modelos de datos (SQLAlchemy)
│   │   │   ├── userModel.py
│   │   │   ├── propertyModel.py
│   │   │   └── imageModel.py
│   │   ├── schemas/            # Validaciones Pydantic
│   │   ├── core/               # Seguridad JWT y Hashing
│   │   └── main.py             # Punto de entrada de la API
│   ├── docs
│   │   ├── inmobiliaria_db.sql # schema DataBase
│   │   └── README.md
│   ├── media/                  # Almacenamiento de imagenes
│   ├── dbMigrations/           # Historial de cambios en DB
│   ├── .env                    # Variables de entorno (Ignorado en Git)
│   └── requirements.txt        # Dependencias de Python
│
├── frontendProyecto
│   ├── public/                 # Archivos estaticos y configuracion PWA
│   │   └── manifest.json       # Identidad de la App en el movil
│   ├── src
│   │   ├── views/              # Vistas de Admin, Advisor y Client
│   │   ├── components/         # Mapas, Cards y UI
│   │   ├── apiServices/        # Clientes Axios por controlador
│   │   └── store/              # Pinia: Auth y Propiedades
│   └── package.json
│
├── .gitignore
└── README.md
