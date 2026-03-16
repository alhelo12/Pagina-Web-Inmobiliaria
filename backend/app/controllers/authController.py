"""
Controller: Authentication

Endpoints para registro y login de usuarios con JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dbConfig.databaseSession import get_db
from app.services import authService, userService
from app.core.security import create_token_for_user
from app.core.dependencies import get_current_user
from app.schemas import (
    UserCreate,
    ClientRegister,
    UserResponse,
    Token,
    PasswordChange
)
from app.models import User

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
    - **password**: Contraseña (mínimo 8 caracteres, letra y número)
    - **phone**: Teléfono (opcional)
    - **role_id**: ID del rol (1=admin, 2=advisor, 3=client)
    
    Validaciones:
    - Email único
    - Contraseña con requisitos mínimos
    - Rol debe existir
    
    Retorna el usuario creado (sin token).
    Para obtener token, hacer login después del registro.
    """
    user = authService.register_user(db, user_data)
    return user

@router.post("/register/client", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_client(
    client_data: ClientRegister,  # ← CAMBIAR de UserCreate a ClientRegister
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo cliente (registro público)
    
    NO requiere role_id (se asigna automáticamente como 'client').
    
    - **full_name**: Nombre completo
    - **email**: Email único
    - **password**: Contraseña (mínimo 8 caracteres)
    - **phone**: Teléfono (opcional)
    
    Retorna el usuario creado (sin token).
    Para obtener token, hacer login después del registro.
    """
    # Convertir ClientRegister a UserCreate con role_id=3
    from app.models import Role
    
    # Obtener el rol 'client'
    client_role = db.query(Role).filter(Role.name == 'client').first()
    if not client_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración: rol 'client' no existe"
        )
    
    # Crear UserCreate con role_id
    user_create_data = UserCreate(
        full_name=client_data.full_name,
        email=client_data.email,
        password=client_data.password,
        phone=client_data.phone,
        role_id=client_role.id
    )
    
    user = authService.register_user(db, user_create_data)
    return user



# ==========================================
# LOGIN
# ==========================================

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login de usuario (retorna token JWT)
    
    Usa OAuth2PasswordRequestForm (estándar OAuth2):
    - **username**: Email del usuario
    - **password**: Contraseña
    
    Retorna:
    - **access_token**: Token JWT
    - **token_type**: "bearer"
    
    Para usar el token en otros endpoints:
```
    Authorization: Bearer <access_token>
```
    
    Errores:
    - 401: Credenciales incorrectas
    - 403: Usuario inactivo
    """
    # OAuth2PasswordRequestForm usa "username" pero nosotros usamos email
    user = authService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador."
        )
    
    # Crear token JWT
    access_token = create_token_for_user(
        user_id=user.id,
        email=user.email,
        role_name=user.role.name
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================
# OBTENER USUARIO ACTUAL
# ==========================================

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener información del usuario autenticado
    
    Requiere token JWT en header:
```
    Authorization: Bearer <token>
```
    
    Retorna:
    - Información completa del usuario autenticado
    
    Errores:
    - 401: Token inválido o expirado
    - 403: Usuario inactivo
    """
    return current_user


# ==========================================
# CAMBIO DE CONTRASEÑA
# ==========================================

@router.post("/change-password", response_model=UserResponse)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña de usuario autenticado
    
    Requiere token JWT en header.
    
    Body:
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña
    
    Validaciones:
    - Contraseña actual correcta
    - Nueva contraseña cumple requisitos
    - Nueva contraseña diferente a la actual
    
    Errores:
    - 401: Token inválido o contraseña actual incorrecta
    - 400: Nueva contraseña inválida
    
    Nota: user_id se extrae del token JWT automáticamente.
    """
    user = authService.change_password(
        db,
        current_user.id,  # Extraído del token
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
        