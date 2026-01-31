from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# El engine es el que realmente se conecta a la DB
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cada instancia de SessionLocal será una conexión real
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para probar la conexión
def test_db_connection():
    try:
        # Intenta conectar físicamente
        connection = engine.connect()
        print("--- CONEXION A BASE DE DATOS: EXITOSA ---")
        connection.close()
    except Exception as e:
        print("--- ERROR DE CONEXION A BASE DE DATOS ---")
        print(f"Detalle: {e}")
        