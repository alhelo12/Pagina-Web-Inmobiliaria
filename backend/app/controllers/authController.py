"""
Controller: Authentication

Endpoints para registro y login de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dbConfig.databaseSession import get_db
from app.services import authService, userService
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    PasswordChange
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# REGISTRO
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario
    
    - **full_name**: Nombre completo
    - **email**: Email único
    - **password**: Contraseña (mínimo 8 caracteres)
    - **phone**: Teléfono (opcional)
    - **role_id**: ID del rol (1=admin, 2=advisor, 3=client)
    
    Validaciones:
    - Email único
    - Contraseña con requisitos mínimos
    - Rol debe existir
    """
    user = authService.register_user(db, user_data)
    return user


@router.post("/register/client", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_client(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo cliente (registro público)
    
    Igual que /register pero fuerza role_id = 3 (client).
    Útil para registro público donde el usuario no elige su rol.
    
    - **full_name**: Nombre completo
    - **email**: Email único
    - **password**: Contraseña (mínimo 8 caracteres)
    - **phone**: Teléfono (opcional)
    """
    user = authService.register_client(db, user_data)
    return user


# ==========================================
# LOGIN
# ==========================================

@router.post("/login", response_model=UserResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login de usuario
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Retorna:
    - Usuario autenticado con sus datos
    
    Errores:
    - 401: Credenciales incorrectas
    - 403: Usuario inactivo
    
    Nota: Por ahora retorna el usuario completo.
    Cuando se implemente JWT, retornará un token.
    """
    user = authService.login(db, credentials)
    return user


# ==========================================
# CAMBIO DE CONTRASEÑA
# ==========================================

@router.post("/change-password", response_model=UserResponse)
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña de usuario
    
    - **user_id**: ID del usuario
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña
    
    Validaciones:
    - Contraseña actual correcta
    - Nueva contraseña cumple requisitos
    - Nueva contraseña diferente a la actual
    
    Nota: Por ahora requiere user_id en el body.
    Con JWT, se extraerá del token automáticamente.
    """
    user = authService.change_password(
        db,
        password_data.user_id,
        password_data.current_password,
        password_data.new_password
    )
    return user


# ==========================================
# VALIDACIONES
# ==========================================

@router.get("/check-email")
def check_email_available(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Verificar si un email está disponible
    
    Útil para validación en tiempo real en el frontend.
    
    - **email**: Email a verificar
    
    Retorna:
    - available: True si está disponible, False si ya existe
    """
    available = authService.validate_email_available(db, email)
    return {
        "email": email,
        "available": available
    }


@router.get("/validate-password")
def validate_password(password: str):
    """
    Validar requisitos de contraseña
    
    Útil para feedback en tiempo real en el frontend.
    
    - **password**: Contraseña a validar
    
    Retorna:
    - valid: True si cumple requisitos
    - errors: Lista de errores si no cumple
    """
    try:
        authService.validate_password_strength(password)
        return {
            "valid": True,
            "errors": []
        }
    except HTTPException as e:
        return {
            "valid": False,
            "errors": [e.detail]
        }
        