"""
FastAPI Main Application
Sistema Inmobiliario - Backend API
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from sqlalchemy import func

from app.dbConfig.databaseSession import get_db, get_pool_status, test_db_connection
from app.models import Property, User, Role
from app.schemas import PropertyResponse

# ==========================================
# IMPORTAR ROUTERS
# ==========================================
from app.controllers.authController import router as auth_router
from app.controllers.userController import router as user_router

# Ejecutar prueba al iniciar
test_db_connection()

# Cargar variables de entorno al inicio
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="Inmobiliaria API",
    description="API para sistema inmobiliario con aprobación de propiedades",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# INCLUIR ROUTERS
# ==========================================
app.include_router(auth_router)
app.include_router(user_router)

# ==========================================
# ENDPOINTS DE PRUEBA
# ==========================================

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raíz - Hello World
    
    Verifica que la API está funcionando.
    """
    return {
        "message": "Inmobiliaria API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check básico
    
    Verifica que el servidor está funcionando.
    """
    return {
        "status": "healthy",
        "service": "inmobiliaria-api"
    }


@app.get("/health/db", tags=["Health"])
def health_check_database():
    """
    Health check con verificación de base de datos
    
    Verifica:
    - Conexión a PostgreSQL
    - Estado del connection pool
    """
    db_connected = test_db_connection()
    pool_stats = get_pool_status() if db_connected else None
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": {
            "connected": db_connected,
            "type": "postgresql"
        },
        "connection_pool": pool_stats
    }


@app.get("/test/roles", tags=["Test"])
def test_roles(db: Session = Depends(get_db)):
    """
    Endpoint de prueba - Listar roles
    
    Verifica:
    - Conexión a BD
    - Modelo Role funciona
    - Query básico funciona
    """
    roles = db.query(Role).all()
    return {
        "total": len(roles),
        "roles": [{"id": r.id, "name": r.name} for r in roles]
    }


@app.get("/test/users", tags=["Test"])
def test_users(db: Session = Depends(get_db)):
    """
    Endpoint de prueba - Contar usuarios
    """
    total_users = db.query(User).count()
    users_by_role = db.query(Role.name, func.count(User.id))\
        .join(User, Role.id == User.role_id, isouter=True)\
        .group_by(Role.name)\
        .all()
    
    return {
        "total_users": total_users,
        "by_role": {role: count for role, count in users_by_role}
    }


@app.get("/test/properties", response_model=list[PropertyResponse], tags=["Test"])
def test_properties(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba - Listar propiedades
    
    Verifica:
    - Modelo Property funciona
    - Schema PropertyResponse funciona
    - Serialización funciona
    - Relaciones (images) se cargan correctamente
    
    Query params:
    - limit: número máximo de propiedades (default: 10)
    """
    properties = db.query(Property).limit(limit).all()
    return properties


@app.get("/test/properties/{property_id}", response_model=PropertyResponse, tags=["Test"])
def test_property_detail(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba - Detalle de propiedad
    
    Verifica:
    - Query por ID funciona
    - Relaciones se cargan
    - 404 si no existe
    """
    property = db.query(Property).filter(Property.id == property_id).first()
    
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    return property


@app.get("/test/stats", tags=["Test"])
def test_stats(db: Session = Depends(get_db)):
    """
    Endpoint de prueba - Estadísticas generales
    
    Verifica:
    - Queries agregadas funcionan
    - Múltiples modelos funcionan juntos
    """
    from app.models import Advisor, Appointment, Favorite
    
    stats = {
        "users": {
            "total": db.query(User).count(),
            "active": db.query(User).filter(User.is_active == True).count(),
            "inactive": db.query(User).filter(User.is_active == False).count()
        },
        "advisors": {
            "total": db.query(Advisor).count()
        },
        "properties": {
            "total": db.query(Property).count(),
            "approved": db.query(Property).filter(Property.status == 'approved').count(),
            "pending": db.query(Property).filter(Property.status == 'pending').count(),
            "rejected": db.query(Property).filter(Property.status == 'rejected').count(),
            "sold": db.query(Property).filter(Property.status == 'sold').count()
        },
        "appointments": {
            "total": db.query(Appointment).count(),
            "pending": db.query(Appointment).filter(Appointment.status == 'pending').count(),
            "confirmed": db.query(Appointment).filter(Appointment.status == 'confirmed').count(),
            "completed": db.query(Appointment).filter(Appointment.status == 'completed').count()
        },
        "favorites": {
            "total": db.query(Favorite).count()
        }
    }
    
    return stats


# ==========================================
# EVENT HANDLERS
# ==========================================

@app.on_event("startup")
async def startup_event():
    """
    Evento al iniciar la aplicación
    
    Verifica la conexión a la base de datos.
    """
    print("="*80)
    print("🚀 Iniciando Inmobiliaria API...")
    print("="*80)
    
    if test_db_connection():
        print("✅ Conexión a PostgreSQL: OK")
        pool = get_pool_status()
        print(f"📊 Connection Pool: {pool['pool_size']} conexiones disponibles")
    else:
        print("❌ Error: No se pudo conectar a PostgreSQL")
    
    print("="*80)
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("="*80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento al cerrar la aplicación
    """
    print("👋 Cerrando Inmobiliaria API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    