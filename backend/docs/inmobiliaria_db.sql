-- ==========================================
-- SISTEMA INMOBILIARIO - SCHEMA DATABASE
-- Version: 1.4.0
-- Descripción: Base de datos para sistema de gestión inmobiliaria
--              con sistema de aprobación de propiedades, chat cliente-asesor,
--              seguimiento post-venta y asignación formal cliente-asesor
-- ==========================================

-- ==========================================
-- 1. FUNCIÓN PARA ACTUALIZAR TIMESTAMPS
-- ==========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ==========================================
-- 2. TABLAS PRINCIPALES
-- ==========================================

-- Tabla: roles
-- Descripción: Define los tipos de usuarios del sistema
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: users
-- Descripción: Usuarios generales del sistema
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash TEXT NOT NULL,
    role_id INT REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: advisors
-- Descripción: Perfil extendido para usuarios con rol de asesor
CREATE TABLE IF NOT EXISTS advisors (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    license_number VARCHAR(50),
    agency_name VARCHAR(100),
    profile_picture TEXT,
    rating DECIMAL(3,2) DEFAULT 5.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: properties
-- Descripción: Propiedades publicadas en el sistema
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(12,2) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(50) DEFAULT 'sale', -- sale | rent
    
    -- Ubicación
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    
    -- Características
    bedrooms INT DEFAULT 0,
    bathrooms INT DEFAULT 0,
    square_meters INT DEFAULT 0,
    
    -- Control de aprobación
    status VARCHAR(50) DEFAULT 'pending', -- pending | approved | rejected | sold
    submitted_by_user_id INT REFERENCES users(id),
    advisor_id INT REFERENCES advisors(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: property_images
-- Descripción: Imágenes asociadas a las propiedades
CREATE TABLE IF NOT EXISTS property_images (
    id SERIAL PRIMARY KEY,
    property_id INT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    label VARCHAR(100),
    image_type VARCHAR(50) DEFAULT 'general' NOT NULL,
    is_extra BOOLEAN DEFAULT FALSE NOT NULL,
    is_main BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: appointments
-- Descripción: Citas entre clientes y asesores
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT NOT NULL REFERENCES advisors(id) ON DELETE CASCADE,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    
    appointment_type VARCHAR(50) DEFAULT 'viewing', -- viewing | inspection
    scheduled_date TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending | confirmed | completed | cancelled
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: favorites
-- Descripción: Propiedades marcadas como favoritas por los usuarios
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    property_id INT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT unique_favorite UNIQUE (user_id, property_id)
);

-- Tabla: notifications
-- Descripción: Notificaciones para informar a los clientes sobre el estado de sus propiedades
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    property_id INT REFERENCES properties(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'info',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: conversations
-- Descripción: Hilo de chat entre cliente y su asesor asignado
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT NOT NULL REFERENCES advisors(id) ON DELETE CASCADE,
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT unique_conversation UNIQUE (user_id, advisor_id)
);

-- Tabla: messages
-- Descripción: Mensajes individuales dentro de una conversación
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
-- Descripción: Seguimiento automatizado después de que una propiedad es vendida/rentada
-- Tipos: satisfaction_survey (+7 días), check_in_call (+30), referral_request (+60), maintenance_reminder (+90)
CREATE TABLE IF NOT EXISTS post_sale_followups (
    id SERIAL PRIMARY KEY,
    property_id INT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    client_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT REFERENCES advisors(id) ON DELETE SET NULL,
    sale_date TIMESTAMP NOT NULL,
    followup_type VARCHAR(50) NOT NULL, -- satisfaction_survey | check_in_call | referral_request | maintenance_reminder
    scheduled_date TIMESTAMP NOT NULL,
    completed_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending', -- pending | completed | skipped
    notes TEXT,
    satisfaction_score SMALLINT CHECK (satisfaction_score BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla: client_advisor_assignments
-- Descripción: Relación formal entre un cliente y un asesor inmobiliario
CREATE TABLE IF NOT EXISTS client_advisor_assignments (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advisor_id INT NOT NULL REFERENCES advisors(id) ON DELETE CASCADE,
    assigned_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- active | inactive
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ==========================================
-- 3. ÍNDICES PARA OPTIMIZACIÓN
-- ==========================================

-- Índices en roles
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Índices en users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Índices en properties
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_advisor_id ON properties(advisor_id);

-- Índices en property_images
CREATE INDEX IF NOT EXISTS idx_property_images_property_id ON property_images(property_id);
CREATE INDEX IF NOT EXISTS idx_property_images_is_main ON property_images(is_main);
CREATE INDEX IF NOT EXISTS idx_property_images_is_extra ON property_images(is_extra);
CREATE INDEX IF NOT EXISTS idx_property_images_image_type ON property_images(image_type);

-- Índices en favorites
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_property_id ON favorites(property_id);

-- Índices en appointments
CREATE INDEX IF NOT EXISTS idx_appointments_client_id ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_appointments_advisor_id ON appointments(advisor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled_date ON appointments(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- Índices en conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_advisor_id ON conversations(advisor_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC NULLS LAST);

-- Índices en messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read) WHERE is_read = FALSE;

-- Índices en post_sale_followups
CREATE INDEX IF NOT EXISTS idx_post_sale_property_id ON post_sale_followups(property_id);
CREATE INDEX IF NOT EXISTS idx_post_sale_client_id ON post_sale_followups(client_id);
CREATE INDEX IF NOT EXISTS idx_post_sale_advisor_id ON post_sale_followups(advisor_id);
CREATE INDEX IF NOT EXISTS idx_post_sale_status ON post_sale_followups(status);
CREATE INDEX IF NOT EXISTS idx_post_sale_followup_type ON post_sale_followups(followup_type);
CREATE INDEX IF NOT EXISTS idx_post_sale_scheduled_date ON post_sale_followups(scheduled_date);

-- Índices en client_advisor_assignments
CREATE INDEX IF NOT EXISTS idx_client_advisor_client_id ON client_advisor_assignments(client_id);
CREATE INDEX IF NOT EXISTS idx_client_advisor_advisor_id ON client_advisor_assignments(advisor_id);
CREATE INDEX IF NOT EXISTS idx_client_advisor_status ON client_advisor_assignments(status);

-- ==========================================
-- 4. TRIGGERS
-- ==========================================

-- Trigger: Actualizar updated_at en roles
CREATE TRIGGER tr_update_roles 
    BEFORE UPDATE ON roles 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en users
CREATE TRIGGER tr_update_users 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en advisors
CREATE TRIGGER tr_update_advisors 
    BEFORE UPDATE ON advisors 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en properties
CREATE TRIGGER tr_update_properties 
    BEFORE UPDATE ON properties 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en property_images
CREATE TRIGGER tr_update_property_images 
    BEFORE UPDATE ON property_images 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en appointments
CREATE TRIGGER tr_update_appointments 
    BEFORE UPDATE ON appointments 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en favorites
CREATE TRIGGER tr_update_favorites
    BEFORE UPDATE ON favorites
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en conversations
CREATE TRIGGER tr_update_conversations
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en messages
CREATE TRIGGER tr_update_messages
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en post_sale_followups
CREATE TRIGGER tr_update_post_sale_followups
    BEFORE UPDATE ON post_sale_followups
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger: Actualizar updated_at en client_advisor_assignments
CREATE TRIGGER tr_update_client_advisor_assignments
    BEFORE UPDATE ON client_advisor_assignments
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- ==========================================
-- 5. DATOS INICIALES (SEED)
-- ==========================================

-- Insertar roles predeterminados
INSERT INTO roles (name) VALUES ('admin'), ('advisor'), ('client')
ON CONFLICT (name) DO NOTHING;

-- ==========================================
-- USUARIO ADMIN INICIAL
-- Email:    admin@inmobiliaria.com
-- Password: Admin123
-- ==========================================
INSERT INTO users (full_name, email, password_hash, role_id, is_active)
VALUES (
    'Administrador',
    'admin@inmobiliaria.com',
    '$2b$12$OwBu/NizswHOVyhOB1Yw..VcDP/1ZyL2YAU9Y9F/vADHtjSzXDy76',
    (SELECT id FROM roles WHERE name = 'admin'),
    true
)
ON CONFLICT (email) DO NOTHING;

-- ==========================================
-- 6. COMENTARIOS EN TABLAS (DOCUMENTACIÓN)
-- ==========================================

COMMENT ON TABLE roles IS 'Tipos de usuarios del sistema';
COMMENT ON TABLE users IS 'Usuarios generales del sistema';
COMMENT ON TABLE advisors IS 'Perfil extendido para asesores inmobiliarios';
COMMENT ON TABLE properties IS 'Propiedades listadas en el sistema';
COMMENT ON TABLE property_images IS 'Galería de imágenes de las propiedades';
COMMENT ON TABLE appointments IS 'Citas programadas entre clientes y asesores';
COMMENT ON TABLE favorites IS 'Propiedades guardadas como favoritas por los usuarios';
COMMENT ON TABLE conversations IS 'Hilos de chat entre clientes y sus asesores asignados';
COMMENT ON TABLE messages IS 'Mensajes individuales dentro de una conversación';
COMMENT ON TABLE post_sale_followups IS 'Seguimiento automatizado post-venta (encuestas, llamadas, referidos, mantenimiento)';
COMMENT ON TABLE client_advisor_assignments IS 'Relación formal entre clientes y asesores inmobiliarios';

-- ==========================================
-- FIN DEL SCRIPT
-- ==========================================
