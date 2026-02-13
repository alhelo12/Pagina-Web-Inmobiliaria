"""
Modelo: Favorite (Propiedades Favoritas)

Descripción:
    Relación entre usuarios y propiedades marcadas como favoritas.
    Permite a los usuarios guardar propiedades de interés para
    consultarlas más tarde.

Tabla: favorites

Constraints:
    - Un usuario no puede marcar la misma propiedad como favorita dos veces
    - unique constraint en (user_id, property_id)

Relaciones:
    - user: Many-to-One con User
    - property: Many-to-One con Property
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Favorite(BaseModel):
    """
    Modelo de Favorito
    
    Attributes:
        id (int): ID único del favorito (heredado)
        user_id (int): FK a users
        property_id (int): FK a properties
        created_at (datetime): Fecha en que se marcó como favorita (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        user: Usuario que marcó la propiedad como favorita
        property: Propiedad marcada como favorita
    
    Constraints:
        - Unique constraint en (user_id, property_id)
    """
    __tablename__ = "favorites"
    
    # ==========================================
    # CAMPOS
    # ==========================================
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al usuario"
    )
    
    property_id = Column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a la propiedad"
    )
    
    # ==========================================
    # CONSTRAINTS
    # ==========================================
    
    __table_args__ = (
        UniqueConstraint('user_id', 'property_id', name='unique_favorite'),
    )
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación Many-to-One con User
    user = relationship(
        "User",
        back_populates="favorites"
    )
    
    # Relación Many-to-One con Property
    # NOTA: No puede llamarse "property" para evitar conflicto con @property
    favorited_property = relationship(
        "Property",
        back_populates="favorites"
    )
    
    def __repr__(self):
        """Representación del favorito para debugging"""
        return f"<Favorite(id={self.id}, user_id={self.user_id}, property_id={self.property_id})>"
    