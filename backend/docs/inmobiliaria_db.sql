-- ==========================================
-- SISTEMA INMOBILIARIO - SCHEMA DATABASE
-- Version: 2.0.0 (compatible con migración Alembic 1751639a973d)
-- Descripción: Base de datos para sistema de gestión inmobiliaria
--              con sistema de aprobación de propiedades, chat cliente-asesor,
--              seguimiento post-venta, asignación formal cliente-asesor,
--              notificaciones en tiempo real y formulario público de contacto
-- ==========================================

-- ==========================================
-- 1. EXTENSIONES Y FUNCIONES
-- ==========================================

-- Extensión para UUID (opcional, para futuras migraciones)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ==========================================
-- 2. TIPOS ENUM (fuente de verdad para el backend)
-- ==========================================

CREATE TYPE role_enum AS ENUM ('admin', 'advisor', 'client');
CREATE TYPE property_status_enum AS ENUM ('pending', 'approved', 'rejected', 'sold');
CREATE TYPE property_type_enum AS ENUM ('house', 'apartment', 'land', 'commercial', 'office');
CREATE TYPE transaction_type_enum AS ENUM ('sale', 'rent');
CREATE TYPE appointment_status_enum AS ENUM ('pending', 'confirmed', 'completed', 'cancelled');
CREATE TYPE appointment_type_enum AS ENUM ('visit', 'video_call', 'phone_call');
CREATE TYPE notification_type_enum AS ENUM (
    'property_approved', 'property_rejected', 'property_sold',
    'new_appointment', 'appointment_confirmed', 'appointment_cancelled', 'appointment_completed',
    'new_message', 'post_sale_followup', 'contact_inquiry', 'system_alert'
);
CREATE TYPE followup_type_enum AS ENUM ('call', 'email', 'visit', 'whatsapp');
CREATE TYPE followup_status_enum AS ENUM ('pending', 'completed', 'skipped');

-- ==========================================
-- 3. TABLAS PRINCIPALES
-- ==========================================

-- Tabla: roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name role_enum UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role_id INT REFERENCES roles(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    user_preferences JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: advisors
CREATE TABLE IF NOT EXISTS advisors (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    license_number VARCHAR(50) UNIQUE,
    agency_name VARCHAR(100),
    profile_picture VARCHAR(255),
    rating NUMERIC(3,2) DEFAULT 5.00 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: properties
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    price NUMERIC(12,2) NOT NULL,
    property_type property_type_enum NOT NULL,
    transaction_type transaction_type_enum NOT NULL,
    status property_status_enum DEFAULT 'pending' NOT NULL,
    address VARCHAR(300) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    bedrooms INT,
    bathrooms INT,
    square_meters NUMERIC(10,2),
    parking_spaces INT,
    year_built INT,
    has_garden BOOLEAN DEFAULT FALSE,
    has_pool BOOLEAN DEFAULT FALSE,
    has_air_conditioning BOOLEAN DEFAULT FALSE,
    has_heating BOOLEAN DEFAULT FALSE,
    submitted_by_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    advisor_id INT REFERENCES advisors(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: property_images
CREATE TABLE IF NOT EXISTS property_images (
    id SERIAL PRIMARY KEY,
    property_id INT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    is_main BOOLEAN DEFAULT FALSE NOT NULL,
    label VARCHAR(100),
    is_extra BOOLEAN DEFAULT FALSE NOT NULL,
    image_type VARCHAR(50) DEFAULT 'general' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: appointments
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT NOT NULL REFERENCES advisors(id) ON DELETE CASCADE,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMP NOT NULL,
    duration_minutes INT DEFAULT 60 NOT NULL,
    status appointment_status_enum DEFAULT 'pending' NOT NULL,
    appointment_type appointment_type_enum DEFAULT 'visit' NOT NULL,
    notes TEXT,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: favorites
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    property_id INT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT unique_favorite UNIQUE (user_id, property_id)
);

-- Tabla: notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type_enum NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    property_id INT REFERENCES properties(id) ON DELETE SET NULL,
    appointment_id INT REFERENCES appointments(id) ON DELETE SET NULL,
    followup_id INT REFERENCES post_sale_followups(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: conversations
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT NOT NULL REFERENCES advisors(id) ON DELETE CASCADE,
    property_id INT REFERENCES properties(id) ON DELETE SET NULL,
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_conversation_user_advisor UNIQUE (user_id, advisor_id)
);

-- Tabla: messages
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: post_sale_followups
CREATE TABLE IF NOT EXISTS post_sale_followups (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT REFERENCES advisors(id) ON DELETE SET NULL,
    property_id INT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    followup_type followup_type_enum NOT NULL,
    status followup_status_enum DEFAULT 'pending' NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,
    completed_date TIMESTAMP,
    notes TEXT,
    skip_reason TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: client_advisor_assignments
CREATE TABLE IF NOT EXISTS client_advisor_assignments (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT NOT NULL REFERENCES advisors(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_client_active_advisor UNIQUE (client_id, is_active) WHERE is_active = TRUE
);

-- Tabla: activity_logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: contact_inquiries
CREATE TABLE IF NOT EXISTS contact_inquiries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    service VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ==========================================
-- 4. ÍNDICES PARA OPTIMIZACIÓN
-- ==========================================

-- roles
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- advisors
CREATE INDEX IF NOT EXISTS idx_advisors_user_id ON advisors(user_id);

-- properties
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_transaction_type ON properties(transaction_type);
CREATE INDEX IF NOT EXISTS idx_properties_advisor_id ON properties(advisor_id);
CREATE INDEX IF NOT EXISTS idx_properties_submitted_by_user_id ON properties(submitted_by_user_id);
CREATE INDEX IF NOT EXISTS idx_properties_created_at ON properties(created_at DESC);

-- property_images
CREATE INDEX IF NOT EXISTS idx_property_images_property_id ON property_images(property_id);
CREATE INDEX IF NOT EXISTS idx_property_images_is_main ON property_images(is_main);
CREATE INDEX IF NOT EXISTS idx_property_images_is_extra ON property_images(is_extra);
CREATE INDEX IF NOT EXISTS idx_property_images_image_type ON property_images(image_type);

-- favorites
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_property_id ON favorites(property_id);

-- appointments
CREATE INDEX IF NOT EXISTS idx_appointments_client_id ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_appointments_advisor_id ON appointments(advisor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_property_id ON appointments(property_id);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled_date ON appointments(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_advisor_id ON conversations(advisor_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC NULLS LAST);

-- messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read) WHERE is_read = FALSE;

-- post_sale_followups
CREATE INDEX IF NOT EXISTS idx_post_sale_property_id ON post_sale_followups(property_id);
CREATE INDEX IF NOT EXISTS idx_post_sale_client_id ON post_sale_followups(client_id);
CREATE INDEX IF NOT EXISTS idx_post_sale_advisor_id ON post_sale_followups(advisor_id);
CREATE INDEX IF NOT EXISTS idx_post_sale_status ON post_sale_followups(status);
CREATE INDEX IF NOT EXISTS idx_post_sale_followup_type ON post_sale_followups(followup_type);
CREATE INDEX IF NOT EXISTS idx_post_sale_scheduled_date ON post_sale_followups(scheduled_date);

-- client_advisor_assignments
CREATE INDEX IF NOT EXISTS idx_client_advisor_client_id ON client_advisor_assignments(client_id);
CREATE INDEX IF NOT EXISTS idx_client_advisor_advisor_id ON client_advisor_assignments(advisor_id);
CREATE INDEX IF NOT EXISTS idx_client_advisor_is_active ON client_advisor_assignments(is_active);

-- activity_logs
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);

-- contact_inquiries
CREATE INDEX IF NOT EXISTS idx_contact_inquiries_status ON contact_inquiries(status);
CREATE INDEX IF NOT EXISTS idx_contact_inquiries_email ON contact_inquiries(email);
CREATE INDEX IF NOT EXISTS idx_contact_inquiries_created_at ON contact_inquiries(created_at DESC);

-- ==========================================
-- 5. TRIGGERS PARA updated_at
-- ==========================================

CREATE TRIGGER tr_update_roles
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_users
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_advisors
    BEFORE UPDATE ON advisors
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_properties
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_property_images
    BEFORE UPDATE ON property_images
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_appointments
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_favorites
    BEFORE UPDATE ON favorites
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_notifications
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_conversations
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_messages
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_post_sale_followups
    BEFORE UPDATE ON post_sale_followups
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_client_advisor_assignments
    BEFORE UPDATE ON client_advisor_assignments
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_activity_logs
    BEFORE UPDATE ON activity_logs
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER tr_update_contact_inquiries
    BEFORE UPDATE ON contact_inquiries
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- ==========================================
-- 6. DATOS INICIALES (SEED)
-- ==========================================

-- Insertar roles predeterminados (usando ENUM)
INSERT INTO roles (id, name, description) VALUES
    (1, 'admin', 'Administrador del sistema'),
    (2, 'advisor', 'Asesor inmobiliario'),
    (3, 'client', 'Cliente')
ON CONFLICT (id) DO NOTHING;

-- ==========================================
-- USUARIO ADMIN INICIAL
-- IMPORTANTE: No se incluye por seguridad.
-- DEBES crear el usuario admin manualmente tras la instalación:
--   python -c "from app.core.security import hash_password; print(hash_password('TU_PASSWORD_SEGURA'))"
-- Y luego insertar el hash real en la BD.
-- ==========================================
-- INSERT INTO users (full_name, email, password_hash, role_id, is_active)
-- VALUES (
--     'Administrador',
--     'admin@inmobiliaria.com',
--     'REEMPLAZA_CON_HASH_REAL_GENERADO_CON_BCRYPT',
--     (SELECT id FROM roles WHERE name = 'admin'),
--     true
-- )
-- ON CONFLICT (email) DO NOTHING;

-- ==========================================
-- 7. COMENTARIOS EN TABLAS (DOCUMENTACIÓN)
-- ==========================================

COMMENT ON TABLE roles IS 'Tipos de usuarios del sistema';
COMMENT ON TABLE users IS 'Usuarios generales del sistema';
COMMENT ON TABLE advisors IS 'Perfil extendido para asesores inmobiliarios';
COMMENT ON TABLE properties IS 'Propiedades listadas en el sistema';
COMMENT ON TABLE property_images IS 'Galería de imágenes de las propiedades';
COMMENT ON TABLE appointments IS 'Citas programadas entre clientes y asesores';
COMMENT ON TABLE favorites IS 'Propiedades guardadas como favoritas por los usuarios';
COMMENT ON TABLE notifications IS 'Notificaciones en tiempo real para usuarios';
COMMENT ON TABLE conversations IS 'Hilos de chat entre clientes y sus asesores asignados';
COMMENT ON TABLE messages IS 'Mensajes individuales dentro de una conversación';
COMMENT ON TABLE post_sale_followups IS 'Seguimiento automatizado post-venta (encuestas, llamadas, referidos, mantenimiento)';
COMMENT ON TABLE client_advisor_assignments IS 'Relación formal entre clientes y asesores inmobiliarios';
COMMENT ON TABLE activity_logs IS 'Registro de actividad para auditoría y seguridad';
COMMENT ON TABLE contact_inquiries IS 'Consultas públicas recibidas desde el formulario de contacto del sitio web';

-- ==========================================
-- FIN DEL SCRIPT
-- ==========================================