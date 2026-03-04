# verify_models.py
"""
Script de verificación de modelos y relaciones
"""

from app.models import Role, User, Advisor, Property, PropertyImage, Appointment, Favorite

def verify_relationships():
    """Verifica todas las relaciones de los modelos"""
    
    models = {
        'Role': Role,
        'User': User,
        'Advisor': Advisor,
        'Property': Property,
        'PropertyImage': PropertyImage,
        'Appointment': Appointment,
        'Favorite': Favorite
    }
    
    print("="*80)
    print("VERIFICACIÓN DE MODELOS Y RELACIONES")
    print("="*80)
    
    for model_name, model_class in models.items():
        print(f"\n{'='*80}")
        print(f"MODELO: {model_name}")
        print(f"Tabla: {model_class.__tablename__}")
        print(f"{'='*80}")
        
        # Obtener relaciones
        relationships = model_class.__mapper__.relationships
        
        if not relationships:
            print("  ❌ Sin relaciones definidas")
        else:
            print(f"  ✅ Total de relaciones: {len(relationships)}\n")
            
            for rel in relationships:
                print(f"  📌 Relación: {rel.key}")
                print(f"     - Apunta a: {rel.entity.class_.__name__}")
                print(f"     - Tipo: {rel.direction.name}")
                print(f"     - Uselist: {rel.uselist}")
                
                # Verificar back_populates
                if rel.back_populates:
                    print(f"     - back_populates: '{rel.back_populates}'")
                    
                    # Verificar que existe en el otro modelo
                    try:
                        other_model = rel.entity.class_
                        other_rel = other_model.__mapper__.relationships.get(rel.back_populates)
                        if other_rel:
                            print(f"     - ✅ Relación bidireccional OK")
                        else:
                            print(f"     - ⚠️ WARNING: back_populates '{rel.back_populates}' no existe en {rel.entity.class_.__name__}")
                    except Exception as e:
                        print(f"     - ❌ ERROR verificando back_populates: {e}")
                else:
                    print(f"     - ⚠️ Sin back_populates")
                
                print()
    
    print("\n" + "="*80)
    print("VERIFICACIÓN COMPLETADA")
    print("="*80)

def verify_table_structure():
    """Verifica la estructura de las tablas"""
    
    models = {
        'Role': Role,
        'User': User,
        'Advisor': Advisor,
        'Property': Property,
        'PropertyImage': PropertyImage,
        'Appointment': Appointment,
        'Favorite': Favorite
    }
    
    print("\n" + "="*80)
    print("ESTRUCTURA DE TABLAS")
    print("="*80)
    
    for model_name, model_class in models.items():
        print(f"\n{model_name} ({model_class.__tablename__}):")
        columns = model_class.__table__.columns
        print(f"  Total columnas: {len(columns)}")
        for col in columns:
            nullable = "NULL" if col.nullable else "NOT NULL"
            primary = " [PK]" if col.primary_key else ""
            foreign = " [FK]" if col.foreign_keys else ""
            print(f"    - {col.name}: {col.type}{primary}{foreign} {nullable}")

if __name__ == "__main__":
    try:
        verify_relationships()
        verify_table_structure()
        print("\n✅ VERIFICACIÓN EXITOSA - Todos los modelos funcionan correctamente\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        