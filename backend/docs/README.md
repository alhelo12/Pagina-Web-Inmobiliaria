# Database Schema

Base de datos para el sistema inmobiliario.

## Estructura

- **schema.sql**: Script principal para crear todas las tablas
- **seed.sql** (futuro): Datos de prueba
- **migrations/** (futuro): Migraciones con Alembic

## Diagrama de Relaciones
```
users (1) ─────< (N) properties
users (1) ─────< (N) favorites
users (1) ─────< (N) appointments

advisors (1) ──< (N) properties
advisors (1) ──< (N) appointments

properties (1) ─< (N) property_images
properties (1) ─< (N) favorites
properties (1) ─< (N) appointments
```

## Roles del Sistema

- **admin**: Administrador con permisos totales
- **advisor**: Asesor inmobiliario que gestiona propiedades
- **client**: Cliente que busca y/o publica propiedades

## Estados de Propiedades

- **pending**: Esperando aprobación del asesor
- **approved**: Aprobada y visible públicamente
- **rejected**: Rechazada por el asesor
- **sold**: Propiedad vendida/rentada
