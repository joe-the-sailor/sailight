-- =============================================================================
-- SAILIGHT - Datenbank Initialisierung
-- PostgreSQL + PostGIS Schema für Straßenbeleuchtungsverwaltung
-- =============================================================================

-- PostGIS-Erweiterung aktivieren (falls nicht bereits geschehen)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- UUID-Erweiterung für eindeutige IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schema für die Anwendung erstellen
CREATE SCHEMA IF NOT EXISTS sailight;
SET search_path TO sailight, public;

-- Zeitzone für Luxemburg setzen
SET timezone = 'Europe/Luxembourg';

-- =============================================================================
-- Enums (Aufzählungstypen)
-- =============================================================================

-- Status für verschiedene Entitäten
CREATE TYPE status_type AS ENUM (
    'active',
    'inactive',
    'maintenance',
    'faulty',
    'planned',
    'in_progress',
    'completed',
    'draft',
    'sent',
    'paid',
    'overdue',
    'cancelled',
    'new',
    'used',
    'defective',
    'low',
    'medium',
    'high',
    'critical'
);

-- Prioritäten
CREATE TYPE priority_type AS ENUM (
    'low',
    'medium', 
    'high',
    'critical'
);

-- Severity (Schweregrad)
CREATE TYPE severity_type AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Aktions-Typen
CREATE TYPE action_type AS ENUM (
    'CREATE',
    'UPDATE',
    'DELETE',
    'LOGIN',
    'LOGOUT'
);

-- =============================================================================
-- Geografische Hierarchie
-- =============================================================================

-- Länder
CREATE TABLE IF NOT EXISTS country (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    iso_code VARCHAR(2) UNIQUE NOT NULL,
    geom GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Regionen
CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    country_id INTEGER REFERENCES country(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    geom GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Gemeinden
CREATE TABLE IF NOT EXISTS municipality (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    region_id INTEGER REFERENCES region(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    geom GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Straßen
CREATE TABLE IF NOT EXISTS street (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    municipality_id INTEGER REFERENCES municipality(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    street_number_start INTEGER,
    street_number_end INTEGER,
    geom GEOMETRY(LINESTRING, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Benutzer & Rollen
-- =============================================================================

-- Rollen
CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Benutzer
CREATE TABLE IF NOT EXISTS user_table (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Benutzer-Rollen (n:m Beziehung)
CREATE TABLE IF NOT EXISTS user_role (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_table(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES role(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- =============================================================================
-- Infrastruktur: Schaltschränke, Leitungsgruppen, Masten, Leuchtstellen
-- =============================================================================

-- Schaltschränke
CREATE TABLE IF NOT EXISTS cabinet (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    identifier VARCHAR(50) UNIQUE NOT NULL,
    street_id INTEGER REFERENCES street(id) ON DELETE SET NULL,
    geom GEOMETRY(POINT, 4326),
    status status_type DEFAULT 'active',
    voltage_level VARCHAR(20),
    installation_date DATE,
    responsible_user_id INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leitungsgruppen (Abgänge)
CREATE TABLE IF NOT EXISTS circuit_group (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    cabinet_id INTEGER REFERENCES cabinet(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    identifier VARCHAR(50) UNIQUE NOT NULL,
    phase VARCHAR(10),
    fuse_rating INTEGER,
    cable_type_id INTEGER,
    cable_length DECIMAL(10,2),
    status status_type DEFAULT 'active',
    installation_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Masten
CREATE TABLE IF NOT EXISTS pole (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    street_id INTEGER REFERENCES street(id) ON DELETE SET NULL,
    identifier VARCHAR(50) UNIQUE NOT NULL,
    geom GEOMETRY(POINT, 4326),
    height DECIMAL(5,2),
    type_id INTEGER,
    material VARCHAR(50),
    installation_date DATE,
    status status_type DEFAULT 'active',
    owner VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leuchtstellen (POIs)
CREATE TABLE IF NOT EXISTS light_point (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    circuit_group_id INTEGER REFERENCES circuit_group(id) ON DELETE SET NULL,
    pole_id INTEGER REFERENCES pole(id) ON DELETE SET NULL,
    identifier VARCHAR(50) UNIQUE NOT NULL,
    geom GEOMETRY(POINT, 4326),
    status status_type DEFAULT 'active',
    lamp_id INTEGER,
    lamp_count INTEGER DEFAULT 1,
    mounting_height DECIMAL(5,2),
    orientation VARCHAR(20),
    light_type VARCHAR(50),
    power INTEGER,
    installation_date DATE,
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Materialwirtschaft
-- =============================================================================

-- Materialkatalog
CREATE TABLE IF NOT EXISTS material_catalog (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    category VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(100),
    unit VARCHAR(20),
    unit_price DECIMAL(10,2),
    lifespan INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leuchtmittel
CREATE TABLE IF NOT EXISTS lamp (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    material_id INTEGER REFERENCES material_catalog(id) ON DELETE SET NULL,
    identifier VARCHAR(50) UNIQUE,
    type VARCHAR(50) NOT NULL,
    color_temperature INTEGER,
    luminous_flux INTEGER,
    wattage INTEGER,
    purchase_date DATE,
    warranty_expiry DATE,
    status status_type DEFAULT 'new',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Verknüpfung: Material an Leuchtstellen
CREATE TABLE IF NOT EXISTS light_point_material (
    id SERIAL PRIMARY KEY,
    light_point_id INTEGER REFERENCES light_point(id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES material_catalog(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    installation_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Verknüpfung: Material an Schaltschränke
CREATE TABLE IF NOT EXISTS cabinet_material (
    id SERIAL PRIMARY KEY,
    cabinet_id INTEGER REFERENCES cabinet(id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES material_catalog(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    installation_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Energie & Abrechnung
-- =============================================================================

-- Stromzähler
CREATE TABLE IF NOT EXISTS electric_meter (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    cabinet_id INTEGER REFERENCES cabinet(id) ON DELETE CASCADE,
    meter_number VARCHAR(50) UNIQUE NOT NULL,
    meter_type VARCHAR(50),
    installation_date DATE,
    last_calibration_date DATE,
    next_calibration_date DATE,
    status status_type DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zählerstände
CREATE TABLE IF NOT EXISTS meter_reading (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    meter_id INTEGER REFERENCES electric_meter(id) ON DELETE CASCADE,
    reading_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reading_value DECIMAL(12,2) NOT NULL,
    reading_type VARCHAR(20) DEFAULT 'manual',
    recorded_by INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rechnungen
CREATE TABLE IF NOT EXISTS invoice (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    meter_id INTEGER REFERENCES electric_meter(id) ON DELETE SET NULL,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    period_start DATE,
    period_end DATE,
    consumption DECIMAL(12,2),
    unit_price DECIMAL(10,4),
    total_amount DECIMAL(12,2),
    tax_rate DECIMAL(5,2),
    status status_type DEFAULT 'draft',
    payment_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Betrieb & Wartung
-- =============================================================================

-- Störungs-Typen
CREATE TABLE IF NOT EXISTS incident_type (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    severity severity_type DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Störungs-Status
CREATE TABLE IF NOT EXISTS incident_status (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Störungsmeldungen
CREATE TABLE IF NOT EXISTS incident (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    incident_type_id INTEGER REFERENCES incident_type(id) ON DELETE SET NULL,
    incident_status_id INTEGER REFERENCES incident_status(id) ON DELETE SET NULL,
    light_point_id INTEGER REFERENCES light_point(id) ON DELETE SET NULL,
    pole_id INTEGER REFERENCES pole(id) ON DELETE SET NULL,
    cabinet_id INTEGER REFERENCES cabinet(id) ON DELETE SET NULL,
    circuit_group_id INTEGER REFERENCES circuit_group(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    geom GEOMETRY(POINT, 4326),
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reported_by INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    assigned_to INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    priority priority_type DEFAULT 'medium',
    resolution_deadline TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolved_by INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    root_cause TEXT,
    solution TEXT,
    cost DECIMAL(10,2),
    is_accident BOOLEAN DEFAULT FALSE,
    accident_report_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Projekte
-- =============================================================================

-- Projekt-Typen
CREATE TABLE IF NOT EXISTS project_type (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projekt-Status
CREATE TABLE IF NOT EXISTS project_status (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projekte
CREATE TABLE IF NOT EXISTS project (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    project_type_id INTEGER REFERENCES project_type(id) ON DELETE SET NULL,
    project_status_id INTEGER REFERENCES project_status(id) ON DELETE SET NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    identifier VARCHAR(50) UNIQUE NOT NULL,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12,2),
    actual_cost DECIMAL(12,2),
    responsible_user_id INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    municipality_id INTEGER REFERENCES municipality(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projekt-Infrastruktur (Verknüpfung)
CREATE TABLE IF NOT EXISTS project_infrastructure (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project(id) ON DELETE CASCADE,
    cabinet_id INTEGER REFERENCES cabinet(id) ON DELETE CASCADE,
    circuit_group_id INTEGER REFERENCES circuit_group(id) ON DELETE CASCADE,
    pole_id INTEGER REFERENCES pole(id) ON DELETE CASCADE,
    light_point_id INTEGER REFERENCES light_point(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    status status_type DEFAULT 'planned',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Dokumentenmanagement
-- =============================================================================

-- Dokumenten-Typen
CREATE TABLE IF NOT EXISTS document_type (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dokumente
CREATE TABLE IF NOT EXISTS document (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    document_type_id INTEGER REFERENCES document_type(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    light_point_id INTEGER REFERENCES light_point(id) ON DELETE CASCADE,
    pole_id INTEGER REFERENCES pole(id) ON DELETE CASCADE,
    cabinet_id INTEGER REFERENCES cabinet(id) ON DELETE CASCADE,
    circuit_group_id INTEGER REFERENCES circuit_group(id) ON DELETE CASCADE,
    incident_id INTEGER REFERENCES incident(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES project(id) ON DELETE CASCADE,
    invoice_id INTEGER REFERENCES invoice(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Audit-Log
-- =============================================================================

-- Audit-Log für alle Änderungen
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES user_table(id) ON DELETE SET NULL,
    action action_type NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Indizes für Performance
-- =============================================================================

-- Räumliche Indizes für GIS-Abfragen
CREATE INDEX IF NOT EXISTS idx_country_geom ON country USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_region_geom ON region USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_municipality_geom ON municipality USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_street_geom ON street USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_cabinet_geom ON cabinet USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_pole_geom ON pole USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_light_point_geom ON light_point USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_incident_geom ON incident USING GIST(geom);

-- Standard-Indizes für häufige Abfragen
CREATE INDEX IF NOT EXISTS idx_user_table_username ON user_table(username);
CREATE INDEX IF NOT EXISTS idx_user_table_email ON user_table(email);
CREATE INDEX IF NOT EXISTS idx_cabinet_identifier ON cabinet(identifier);
CREATE INDEX IF NOT EXISTS idx_circuit_group_identifier ON circuit_group(identifier);
CREATE INDEX IF NOT EXISTS idx_pole_identifier ON pole(identifier);
CREATE INDEX IF NOT EXISTS idx_light_point_identifier ON light_point(identifier);
CREATE INDEX IF NOT EXISTS idx_light_point_circuit_group ON light_point(circuit_group_id);
CREATE INDEX IF NOT EXISTS idx_light_point_pole ON light_point(pole_id);
CREATE INDEX IF NOT EXISTS idx_circuit_group_cabinet ON circuit_group(cabinet_id);
CREATE INDEX IF NOT EXISTS idx_meter_reading_meter ON meter_reading(meter_id);
CREATE INDEX IF NOT EXISTS idx_meter_reading_date ON meter_reading(reading_date);
CREATE INDEX IF NOT EXISTS idx_incident_status ON incident(incident_status_id);
CREATE INDEX IF NOT EXISTS idx_incident_type ON incident(incident_type_id);
CREATE INDEX IF NOT EXISTS idx_incident_reported_at ON incident(reported_at);
CREATE INDEX IF NOT EXISTS idx_project_status ON project(project_status_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);

-- =============================================================================
-- Trigger für Audit-Log
-- =============================================================================

-- Funktion zum Erstellen von Audit-Logs
CREATE OR REPLACE FUNCTION create_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, ip_address, user_agent)
        VALUES (current_setting('app.current_user_id')::INTEGER, 'DELETE', TG_TABLE_NAME, OLD.id, to_jsonb(OLD), current_setting('app.ip_address'), current_setting('app.user_agent'));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values, ip_address, user_agent)
        VALUES (current_setting('app.current_user_id')::INTEGER, 'UPDATE', TG_TABLE_NAME, NEW.id, to_jsonb(OLD), to_jsonb(NEW), current_setting('app.ip_address'), current_setting('app.user_agent'));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, new_values, ip_address, user_agent)
        VALUES (current_setting('app.current_user_id')::INTEGER, 'CREATE', TG_TABLE_NAME, NEW.id, to_jsonb(NEW), current_setting('app.ip_address'), current_setting('app.user_agent'));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger für wichtige Tabellen
CREATE TRIGGER audit_cabinet_trigger
    AFTER INSERT OR UPDATE OR DELETE ON cabinet
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_circuit_group_trigger
    AFTER INSERT OR UPDATE OR DELETE ON circuit_group
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_pole_trigger
    AFTER INSERT OR UPDATE OR DELETE ON pole
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_light_point_trigger
    AFTER INSERT OR UPDATE OR DELETE ON light_point
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_incident_trigger
    AFTER INSERT OR UPDATE OR DELETE ON incident
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_project_trigger
    AFTER INSERT OR UPDATE OR DELETE ON project
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_document_trigger
    AFTER INSERT OR UPDATE OR DELETE ON document
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_user_trigger
    AFTER INSERT OR UPDATE OR DELETE ON user_table
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

-- =============================================================================
-- Funktion zum Aktualisieren von updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger für alle Tabellen mit updated_at
CREATE TRIGGER update_cabinet_updated_at
    BEFORE UPDATE ON cabinet
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_circuit_group_updated_at
    BEFORE UPDATE ON circuit_group
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_pole_updated_at
    BEFORE UPDATE ON pole
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_light_point_updated_at
    BEFORE UPDATE ON light_point
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON user_table
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_incident_updated_at
    BEFORE UPDATE ON incident
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_project_updated_at
    BEFORE UPDATE ON project
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- Anfangsdaten einfügen (optional)
-- =============================================================================

-- Länder
INSERT INTO country (name, iso_code) VALUES ('Luxemburg', 'LU') ON CONFLICT DO NOTHING;

-- Rollen
INSERT INTO role (name, description) VALUES 
    ('admin', 'Administrator mit allen Rechten'),
    ('technician', 'Techniker für Wartung und Reparaturen'),
    ('clerk', 'Sachbearbeiter für Verwaltung'),
    ('viewer', 'Nur Lesezugriff')
ON CONFLICT DO NOTHING;

-- Störungs-Typen
INSERT INTO incident_type (name, description, severity) VALUES 
    ('Defekte Lampe', 'Leuchtmittel defekt oder nicht funktionierend', 'high'),
    ('Kabelbruch', 'Kabel defekt oder beschädigt', 'critical'),
    ('Mast beschädigt', 'Mast hat strukturelle Schäden', 'high'),
    ('Schaltschrank defekt', 'Schaltschrank funktioniert nicht', 'critical'),
    ('Stromausfall', 'Kein Strom an der Leuchtstelle', 'medium'),
    ('Wartung fällig', 'Regelmäßige Wartung erforderlich', 'low')
ON CONFLICT DO NOTHING;

-- Störungs-Status
INSERT INTO incident_status (name, description) VALUES 
    ('Gemeldet', 'Störung wurde gemeldet'),
    ('In Bearbeitung', 'Techniker arbeitet an der Lösung'),
    ('Erledigt', 'Störung behoben'),
    ('Storniert', 'Störungsmeldung wurde storniert')
ON CONFLICT DO NOTHING;

-- Projekt-Typen
INSERT INTO project_type (name, description) VALUES 
    ('Neubau', 'Neue Straßenbeleuchtung installieren'),
    ('Sanierung', 'Bestehende Beleuchtung sanieren'),
    ('Erweiterung', 'Beleuchtung erweitern'),
    ('Rückbau', 'Beleuchtung entfernen'),
    ('Wartung', 'Regelmäßige Wartungsarbeiten')
ON CONFLICT DO NOTHING;

-- Projekt-Status
INSERT INTO project_status (name, description) VALUES 
    ('Geplant', 'Projekt ist in Planung'),
    ('Genehmigt', 'Projekt wurde genehmigt'),
    ('In Bearbeitung', 'Projekt wird umgesetzt'),
    ('Abgeschlossen', 'Projekt wurde abgeschlossen'),
    ('Storniert', 'Projekt wurde storniert')
ON CONFLICT DO NOTHING;

-- Dokumenten-Typen
INSERT INTO document_type (name, description) VALUES 
    ('Foto', 'Fotografische Dokumentation'),
    ('Prüfprotokoll', 'Prüf- und Abnahmeprotokoll'),
    ('Stromlaufplan', 'Elektrischer Stromlaufplan'),
    ('Rechnung', 'Rechnung für Material oder Dienstleistungen'),
    ('Vertrag', 'Vertragsdokumente'),
    ('Handbuch', 'Bedienungsanleitung oder Handbuch'),
    ('Unfallbericht', 'Bericht über einen Unfall'),
    ('Planungsdokument', 'Planungsunterlagen')
ON CONFLICT DO NOTHING;

-- Materialkatalog (Beispieldaten)
INSERT INTO material_catalog (category, name, description, manufacturer, unit, unit_price, lifespan) VALUES 
    ('Mast', 'Stahlmast 8m', 'Stahlmast mit 8m Höhe', 'Siemens', 'Stück', 1500.00, 30),
    ('Mast', 'Aluminiummast 10m', 'Aluminiummast mit 10m Höhe', 'Philips', 'Stück', 2000.00, 35),
    ('Leuchtmittel', 'LED 100W', 'LED-Leuchtmittel mit 100W', 'OSRAM', 'Stück', 150.00, 10),
    ('Leuchtmittel', 'Natriumdampf 250W', 'Natriumdampflampe 250W', 'Philips', 'Stück', 80.00, 5),
    ('Kabel', 'NYY 5x16mm²', 'Erdkabel 5x16mm²', 'Nexans', 'Meter', 15.00, 40),
    ('Kabel', 'NYY 5x25mm²', 'Erdkabel 5x25mm²', 'Nexans', 'Meter', 25.00, 40),
    ('Sicherung', 'NH-Sicherung 100A', 'NH-Sicherung 100A', 'ABB', 'Stück', 25.00, 20),
    ('Sicherung', 'NH-Sicherung 200A', 'NH-Sicherung 200A', 'ABB', 'Stück', 40.00, 20)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Views für häufige Abfragen
-- =============================================================================

-- View für Leuchtstellen mit vollständigen Informationen
CREATE OR REPLACE VIEW vw_light_point_full AS
SELECT 
    lp.*,
    cg.name AS circuit_group_name,
    cg.identifier AS circuit_group_identifier,
    cb.name AS cabinet_name,
    cb.identifier AS cabinet_identifier,
    p.identifier AS pole_identifier,
    s.name AS street_name,
    m.name AS municipality_name,
    l.type AS lamp_type,
    l.wattage AS lamp_wattage
FROM light_point lp
LEFT JOIN circuit_group cg ON lp.circuit_group_id = cg.id
LEFT JOIN cabinet cb ON cg.cabinet_id = cb.id
LEFT JOIN pole p ON lp.pole_id = p.id
LEFT JOIN street s ON p.street_id = s.id OR cb.street_id = s.id
LEFT JOIN municipality m ON s.municipality_id = m.id
LEFT JOIN lamp l ON lp.lamp_id = l.id;

-- View für Schaltschränke mit Zählerinformationen
CREATE OR REPLACE VIEW vw_cabinet_full AS
SELECT 
    c.*,
    em.meter_number,
    em.meter_type,
    em.installation_date AS meter_installation_date,
    m.name AS municipality_name,
    s.name AS street_name
FROM cabinet c
LEFT JOIN electric_meter em ON c.id = em.cabinet_id
LEFT JOIN street s ON c.street_id = s.id
LEFT JOIN municipality m ON s.municipality_id = m.id;

-- View für aktuelle Störungen
CREATE OR REPLACE VIEW vw_active_incidents AS
SELECT 
    i.*,
    it.name AS incident_type_name,
    it.severity AS incident_severity,
    is.name AS incident_status_name,
    u1.username AS reported_by_username,
    u2.username AS assigned_to_username,
    lp.identifier AS light_point_identifier,
    p.identifier AS pole_identifier,
    c.identifier AS cabinet_identifier
FROM incident i
LEFT JOIN incident_type it ON i.incident_type_id = it.id
LEFT JOIN incident_status is ON i.incident_status_id = is.id
LEFT JOIN user_table u1 ON i.reported_by = u1.id
LEFT JOIN user_table u2 ON i.assigned_to = u2.id
LEFT JOIN light_point lp ON i.light_point_id = lp.id
LEFT JOIN pole p ON i.pole_id = p.id
LEFT JOIN cabinet c ON i.cabinet_id = c.id
WHERE i.incident_status_id NOT IN (
    SELECT id FROM incident_status WHERE name IN ('Erledigt', 'Storniert')
);

-- =============================================================================
-- Kommentar: Datenbank erfolgreich initialisiert
-- =============================================================================

COMMENT ON SCHEMA sailight IS 'Sailight - Straßenbeleuchtungsverwaltung für Administration des Ponts et Chaussées, Luxemburg';

RAISE NOTICE 'Sailight Datenbank wurde erfolgreich initialisiert!';
