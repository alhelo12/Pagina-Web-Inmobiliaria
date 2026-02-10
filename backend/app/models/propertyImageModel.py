"""
Modelo: PropertyImage (Imágenes de Propiedades)

Descripción:
    Galería de imágenes asociadas a una propiedad.
    Cada propiedad puede tener múltiples imágenes,
    pero solo una puede ser la imagen principal (is_main=True).

Tabla: property_images

Relaciones:
    - property: Many-to-One con Property
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class PropertyImage(BaseModel):
    """
    Modelo de Imagen de Propiedad
    
    Attributes:
        id (int): ID único de la imagen (heredado)
        property_id (int): FK a properties
        image_url (str): URL o ruta de la imagen
        is_main (bool): Si es la imagen principal
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        property: Propiedad a la que pertenece esta imagen
    
    Constraints:
        - Solo puede haber una imagen principal por propiedad
        - Al eliminar una propiedad, se eliminan sus imágenes (cascade)
    """
    __tablename__ = "property_images"
    
    # ==========================================
    # CAMPOS
    # ==========================================
    
    property_id = Column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a la propiedad"
    )
    
    image_url = Column(
        String,
        nullable=False,
        comment="URL o ruta del archivo de imagen"
    )
    
    is_main = Column(
        Boolean,
        default=False,
        index=True,
        comment="Si es la imagen principal de la propiedad"
    )
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación Many-to-One con Property
    property = relationship(
        "Property",
        back_populates="images"
    )
    
    def __repr__(self):
        """Representación de la imagen para debugging"""
        main_text = " [MAIN]" if self.is_main else ""
        return f"<PropertyImage(id={self.id}, property_id={self.property_id}{main_text})>"
    
    def set_as_main(self):
        """
        Establece esta imagen como principal.
        
        Nota: Debes asegurarte de quitar is_main=True de otras imágenes
        de la misma propiedad en la lógica de negocio.
        """
        self.is_main = True
    
    def remove_as_main(self):
        """Quita el estatus de imagen principal"""
        self.is_main = False
        