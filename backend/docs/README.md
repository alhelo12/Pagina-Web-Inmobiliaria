# Database Schema

Base de datos del sistema inmobiliario — versión 1.8.0.

## Archivos

- **inmobiliaria_db.sql**: Schema completo con tablas, índices, triggers, restricciones y seed data
- **alembic/versions/**: 11 migraciones gestionadas con Alembic para cambios incrementales

---

## Diagrama de Relaciones

```
roles (1) ─────────────< (N) users
users (1) ─────────────< (N) advisors
users (1) ─────────────< (N) properties
users (1) ─────────────< (N) favorites
users (1) ─────────────< (N) appointments
users (1) ─────────────< (N) conversations (cliente)
users (1) ─────────────< (N) conversations (asesor vía advisor.user_id)
users (1) ─────────────< (N) messages (sender)
users (1) ─────────────< (N) notifications
users (1) ─────────────< (N) activity_logs
users (1) ─────────────< (N) contact_inquiries
users (1) ─────────────< (N) post_sale_followups (vía property.advisor)

advisors (1) ──────────< (N) properties
advisors (1) ──────────< (N) appointments
advisors (1) ──────────< (N) conversations
advisors (1) ──────────< (N) client_advisor_assignments

properties (1) ────────< (N) property_images
properties (1) ────────< (N) favorites
properties (1) ────────< (N) appointments
properties (1) ────────< (N) conversations
properties (1) ────────< (N) post_sale_followups

conversations (1) ─────< (N) messages
```

---

## Tablas (14)

| Tabla | Descripción | Columnas clave |
|-------|------------|----------------|
| `roles` | Roles del sistema | `id`, `name` (admin/advisor/client) |
| `users` | Usuarios + autenticación + email | `id`, `email`, `password_hash`, `role_id`, `is_active`, `is_email_verified`, `user_preferences` (JSON) |
| `advisors` | Perfil extendido de asesores | `id`, `user_id`, `license_number`, `agency_name`, `rating` |
| `properties` | Propiedades con geolocalización | `id`, `title`, `price`, `lat`, `lng`, `status`, `property_type`, `transaction_type`, `city`, `address`, `advisor_id` |
| `property_images` | Imágenes de propiedades | `id`, `property_id`, `image_url`, `label`, `is_extra` |
| `favorites` | Favoritos de clientes | `id`, `user_id`, `property_id` |
| `appointments` | Citas (visitas/inspecciones) | `id`, `user_id`, `property_id`, `advisor_id`, `status`, `appointment_type`, `date`, `notes` |
| `conversations` | Hilos de chat cliente-asesor | `id`, `user_id` (cliente), `advisor_id`, `property_id`, `last_message`, `last_message_at` |
| `messages` | Mensajes individuales del chat | `id`, `conversation_id`, `sender_id`, `content`, `is_read` |
| `notifications` | Notificaciones push internas | `id`, `user_id`, `type`, `title`, `message`, `property_id`, `is_read` |
| `post_sale_followups` | Seguimiento post-venta | `id`, `property_id`, `followup_type`, `status`, `scheduled_date`, `completed_date`, `notes` |
| `client_advisor_assignments` | Asignación cliente-asesor | `id`, `client_id`, `advisor_id`, `status` (active/inactive) |
| `activity_logs` | Auditoría de actividades | `id`, `user_id`, `action`, `resource_type`, `resource_id`, `details` (JSON) |
| `contact_inquiries` | Formularios de contacto | `id`, `name`, `email`, `phone`, `service`, `message`, `status` (new/contacted/closed) |

---

## Enums

| Enum | Valores |
|------|---------|
| `property_statuses` | `pending`, `approved`, `rejected`, `sold` |
| `property_types` | `house`, `apartment`, `land`, `commercial` |
| `transaction_types` | `sale`, `rent` |
| `appointment_statuses` | `pending`, `confirmed`, `completed`, `cancelled` |
| `appointment_types` | `viewing`, `inspection` |
| `followup_types` | `satisfaction_survey`, `check_in_call`, `referral_request`, `maintenance_reminder` |
| `followup_statuses` | `pending`, `completed`, `skipped` |
| `contact_statuses` | `new`, `contacted`, `closed` |
| `notification_types` | `advisor_assigned`, `approved`, `rejected`, `sold`, `property_updated`, `appointment_confirmed`, `appointment_cancelled`, `appointment_reminder`, `post_sale_survey`, `post_sale_checkin`, `message_received` |
| `user_roles` | `admin`, `advisor`, `client` |

> Los enums están definidos como strings en las tablas y como Python Enums en los schemas Pydantic. El endpoint `GET /constants` expone todos los valores al frontend.

---

## Columnas JSON

| Tabla | Columna | Ejemplo |
|-------|---------|---------|
| `users` | `user_preferences` | `{"all": true, "message_received": false, "appointment_reminder": true}` |

`user_preferences` controla qué tipos de notificación recibe cada usuario. Por defecto todas activas (`{"all": true}`).

---

## Triggers

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Aplicado en todas las tablas que tienen columna `updated_at`. Se ejecuta automáticamente en cada `UPDATE`.

---

## Seed Data

El archivo `inmobiliaria_db.sql` incluye datos iniciales:

- **3 roles**: admin (id=1), advisor (id=2), client (id=3)
- **2 asesores**: con propiedades de ejemplo
- **Propiedades**: algunas aprobadas visibles, otras pendientes para demostración
- **Triggers**: función `update_updated_at_column()` y su aplicación en cada tabla

**NOTA**: El usuario administrador inicial NO se incluye en el dump por seguridad. 
Debes crearlo manualmente tras la instalación:
```bash
# Generar hash de contraseña segura
python -c "from app.core.security import hash_password; print(hash_password('TU_PASSWORD_SEGURA'))"
# Insertar en BD con el hash generado
```

Para recargar desde cero:

```bash
psql -U postgres -d inmobiliaria_db -f docs/inmobiliaria_db.sql
alembic upgrade head
```

---

## Migraciones (Alembic)

Las migraciones incrementales están en `backend/alembic/versions/` (11 revisiones).

### Aplicar migraciones

```bash
cd backend
alembic upgrade head
```

### Generar nueva migración

```bash
alembic revision --autogenerate -m "descripción"
```

> **Nota**: Si `autogenerate` se detiene al detectar tablas eliminadas del modelo (como `notification_preferences`), crear la migración manualmente con `op.add_column()` / `op.create_table()`.

### Historial de revisiones

| Revisión | Descripción |
|----------|-------------|
| `605c1a6623a9` | Baseline — esquema inicial |
| `2e15e28e5a25` | Post-sale followups + client-advisor assignments |
| `846f1b9184c5` | Full-text search en properties |
| `7cabdad1336a` | Activity logs |
| `e14ff5ee7ba7` | Alter last_message_at a datetime |
| `339664da3af1` | Unique constraint en conversations |
| `431acf2b8142` | Property_id en conversations |
| `50117421c43a` | Notification preferences table |
| `3643a157ea4e` | Contact inquiries |
| `9a8b7c6d5e4f` | is_email_verified en users |
| `0a1b2c3d4e5f` | **HEAD** — user_preferences (JSON) en users |
