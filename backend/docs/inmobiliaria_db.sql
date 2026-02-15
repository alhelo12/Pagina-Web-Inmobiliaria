-- ==========================================
-- SISTEMA INMOBILIARIO - SCHEMA DATABASE
-- Version: 1.0.1
-- Descripción: Base de datos para sistema de gestión inmobiliaria
--              con sistema de aprobación de propiedades
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
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    
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

-- Índices en favorites
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_property_id ON favorites(property_id);

-- Índices en appointments
CREATE INDEX IF NOT EXISTS idx_appointments_client_id ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_appointments_advisor_id ON appointments(advisor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled_date ON appointments(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

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

-- ==========================================
-- 5. DATOS INICIALES (SEED)
-- ==========================================

-- Insertar roles predeterminados
INSERT INTO roles (name) VALUES ('admin'), ('advisor'), ('client')
ON CONFLICT (name) DO NOTHING;

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

-- ==========================================
-- FIN DEL SCRIPT
-- ==========================================
