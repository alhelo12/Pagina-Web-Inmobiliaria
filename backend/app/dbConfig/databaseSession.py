from sqlalchemy import create_engine, pool, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging
from app.dbConfig.baseModels import Base

load_dotenv()

# Configurar logging para el pool
logging.basicConfig()
logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ==========================================
# CONFIGURACIÓN OPTIMIZADA DE POOLING
# ==========================================

if ENVIRONMENT == "production":
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.QueuePool,
        pool_size=20,                      # Conexiones permanentes
        max_overflow=30,                   # Conexiones adicionales
        pool_recycle=1800,                 # Reciclar cada 30 min
        pool_pre_ping=True,                # Verificar antes de usar
        pool_timeout=30,                   # Timeout al esperar conexión
        echo=False,                        # Sin debug SQL
        echo_pool=False,                   # Sin debug pool
        connect_args={
            "connect_timeout": 10,
            "application_name": "inmobiliaria_api_prod"
        }
    )
else:  # development
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.QueuePool,
        pool_size=5,                       # Menos conexiones en dev
        max_overflow=10,
        pool_recycle=1800,
        pool_pre_ping=True,
        pool_timeout=30,
        echo=True,                         # Ver queries en desarrollo
        echo_pool=False,
        connect_args={
            "connect_timeout": 10,
            "application_name": "inmobiliaria_api_dev"
        }
    )

# Event listeners para monitoreo (opcional, útil para debugging)
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Se ejecuta cuando se crea una nueva conexión"""
    logging.info("Nueva conexión establecida al pool")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Se ejecuta cuando se toma una conexión del pool"""
    logging.debug("Conexión tomada del pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Se ejecuta cuando se devuelve una conexión al pool"""
    logging.debug("Conexión devuelta al pool")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ==========================================
# DEPENDENCY PARA FASTAPI
# ==========================================

def get_db():
    """
    Dependency que provee una sesión de base de datos.
    Se cierra automáticamente al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# UTILIDADES DE MONITOREO
# ==========================================

def get_pool_status():
    """
    Retorna estadísticas del pool de conexiones.
    Útil para debugging y monitoreo.
    """
    return {
        "pool_size": engine.pool.size(),
        "checked_in_connections": engine.pool.checkedin(),
        "checked_out_connections": engine.pool.checkedout(),
        "overflow_connections": engine.pool.overflow(),
        "total_connections": engine.pool.size() + engine.pool.overflow(),
        "max_possible_connections": engine.pool.size() + engine.pool._max_overflow
    }

def test_db_connection():
    try:
        # Intenta conectar físicamente
        connection = engine.connect()
        print("--- CONEXION A BASE DE DATOS: EXITOSA ---")
        connection.close()
    except Exception as e:
        print("--- ERROR DE CONEXION A BASE DE DATOS ---")
        print(f"Detalle: {e}")
    