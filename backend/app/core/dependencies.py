"""
Core: Dependencies

Dependencias de FastAPI para autenticación y autorización.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import decode_access_token
from app.dbConfig.databaseSession import get_db
from app.models import User
from app.services import userService

# ==========================================
# HTTP BEARER SCHEME
# ==========================================

# HTTPBearer muestra un campo simple para pegar el token en Swagger
security = HTTPBearer()


# ==========================================
# OBTENER USUARIO ACTUAL
# ==========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtener usuario actual desde el token JWT
    
    Esta es la dependencia principal para endpoints protegidos.
    
    Args:
        credentials: Credenciales HTTP Bearer (token)
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
        
    Uso:
        @router.get("/protected")
        def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extraer token de las credentials
    token = credentials.credentials
    
    if not token:
        raise credentials_exception
    
    # Decodificar token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extraer user_id del token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Buscar usuario en BD
    user = userService.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Obtener usuario actual (opcional)
    
    Similar a get_current_user pero no falla si no hay token.
    Útil para endpoints públicos que cambian su comportamiento si hay usuario autenticado.
    
    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado o None
        
    Uso:
        @router.get("/public-or-private")
        def endpoint(current_user: Optional[User] = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"Hola {current_user.full_name}"}
            return {"message": "Hola visitante"}
    """
    if not credentials:
        return None
    
    try:
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = userService.get_user_by_id(db, int(user_id))
        if user and user.is_active:
            return user
        
        return None
    except (TypeError, ValueError):
        return None


# ==========================================
# PERMISOS POR ROL — Factory
# ==========================================

def require_role(*roles):
    """
    Factory: retorna una dependencia de FastAPI que valida roles.

    Uso:
        @router.get("/admin")
        def admin_only(current_user: User = Depends(require_role('admin'))):
            ...

        @router.get("/staff")
        def staff_only(current_user: User = Depends(require_role('admin', 'advisor'))):
            ...
    """
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role or current_user.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requieren permisos de {' o '.join(roles)}"
            )
        return current_user
    return _checker

require_admin = require_role('admin')
require_advisor = require_role('advisor')
require_advisor_or_admin = require_role('admin', 'advisor')


# ==========================================
# VERIFICACIÓN DE PROPIEDAD
# ==========================================

def verify_user_owns_resource(
    resource_user_id: int,
    current_user: User
) -> bool:
    """
    Verificar que el usuario sea dueño del recurso O sea admin
    """
    if current_user.is_admin():
        return True

    if resource_user_id == current_user.id:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para acceder a este recurso"
    )
    
