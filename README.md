# 🌟 Sailight - Straßenbeleuchtungsverwaltung

**Professionelle Software-Anwendung für die Verwaltung der öffentlichen Straßenbeleuchtung**

*Entwickelt für die Administration des Ponts et Chaussées in Luxemburg*

---

## 📋 Übersicht

Sailight ist eine umfassende Lösung zur Verwaltung von Straßenbeleuchtungs-Infrastrukturen mit:

- **150.000+ Leuchtstellen (POIs)**
- **2.000+ Schaltschränke** mit hierarchischer Struktur
- **GIS-Integration** für interaktive Karten
- **Multi-User-Betrieb** für gleichzeitigen Zugriff
- **Multi-Window-Workspace** für effizientes Arbeiten
- **Dark Theme** mit orange Akzenten für augenschonenden Dauerbetrieb

---

## 🚀 Schnellstart

### Voraussetzungen

- **Docker** (empfohlen: Docker Desktop)
- **Docker Compose** (Version 2.0+)
- **Python 3.11+** (für lokale Entwicklung)

### Installation mit Docker

```bash
# Repository klonen
git clone https://github.com/joe-the-sailor/sailight.git
cd sailight

# Docker-Container starten
docker-compose up -d

# Datenbank initialisieren (automatisch beim ersten Start)

# Backend und Frontend sind jetzt verfügbar:
# - Backend API: http://localhost:8000
# - API-Dokumentation: http://localhost:8000/api/docs
# - pgAdmin (Datenbank-Verwaltung): http://localhost:5050
```

### Manuelle Installation

```bash
# Python-Umgebung einrichten
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Backend-Abhängigkeiten installieren
cd backend
pip install -r requirements.txt

# Frontend-Abhängigkeiten installieren
cd ../frontend
pip install -r requirements.txt

# Datenbank starten (PostgreSQL + PostGIS)
docker-compose up -d postgres

# Backend starten
cd ../backend
uvicorn app.main:app --reload

# Frontend starten (in einem separaten Terminal)
cd ../frontend
python src/main.py
```

---

## 🏗️ Architektur

### Tech-Stack

| Komponente | Technologie | Beschreibung |
|------------|-------------|--------------|
| **Datenbank** | PostgreSQL + PostGIS | Relationale Datenbank mit GIS-Erweiterung |
| **Backend** | FastAPI (Python 3.11) | Asynchrones REST-API-Framework |
| **Frontend** | PyQt6 (Python) | Desktop-GUI mit Multi-Window-Fähigkeiten |
| **GIS** | Leaflet + OpenStreetMap | Interaktive Kartenvisualisierung |
| **Authentifizierung** | JWT + OAuth2 | Sichere Benutzerauthentifizierung |
| **Caching** | Redis | Performance-Optimierung |
| **Hintergrundaufgaben** | Celery | Asynchrone Aufgabenverarbeitung |

### Systemarchitektur

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client (Desktop)                               │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────────────┐ │
│  │   PyQt6     │    │   PyQt6     │    │   QWebEngineView          │ │
│  │  (Tabelle)  │    │  (Details)  │    │   (Karte + Leaflet)       │ │
│  └─────────────┘    └─────────────┘    └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (HTTPS/REST)
┌─────────────────────────────────────────────────────────────────────┐
│                        Server                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────────────┐ │
│  │  FastAPI    │◄──►│   Redis     │    │   Celery                 │ │
│  │  (API)      │    │  (Cache)    │    │  (Background Jobs)        │ │
│  └─────────────┘    └─────────────┘    └───────────────────────────┘ │
│                              │                                         │
│                              ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                     PostgreSQL + PostGIS                         │ │
│  │  - Hauptdatenbank (Infrastruktur, GIS, Benutzer)                │ │
│  │  - Räumliche Indizes für schnelle GIS-Abfragen                   │ │
│  │  - JSONB für flexible Attribute                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (WMS/WMTS)
┌─────────────────────────────────────────────────────────────────────┐
│  Geoportail Luxembourg / OpenStreetMap (Karten-Hintergrunddaten)    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Projektstruktur

```
sailight/
├── backend/                          # Backend (FastAPI)
│   ├── app/                         # Anwendungscode
│   │   ├── main.py                  # Haupteinstiegspunkt
│   │   ├── config.py                # Konfiguration
│   │   ├── database.py              # Datenbankverbindung
│   │   ├── models/                  # SQLAlchemy-Modelle
│   │   ├── schemas/                 # Pydantic-Schemas
│   │   ├── api/                     # API-Endpunkte
│   │   │   └── v1/                  # API Version 1
│   │   └── utils/                   # Hilfsfunktionen
│   ├── requirements.txt             # Python-Abhängigkeiten
│   └── Dockerfile                   # Docker-Konfiguration
│
├── frontend/                         # Frontend (PyQt6)
│   ├── src/                         # Quellcode
│   │   ├── main.py                  # Haupteinstiegspunkt
│   │   ├── config.py                # Konfiguration
│   │   ├── views/                  # GUI-Ansichten
│   │   ├── models/                 # Datenmodelle
│   │   └── utils/                   # Hilfsfunktionen
│   ├── requirements.txt             # Python-Abhängigkeiten
│   └── Dockerfile                   # Docker-Konfiguration
│
├── database/                         # Datenbank
│   ├── init.sql                     # Datenbank-Initialisierung
│   ├── schema/                      # SQL-Schemas
│   └── migrations/                  # Datenbank-Migrationen
│
├── docker-compose.yml                # Docker-Compose-Konfiguration
├── .env                              # Umgebungsvariablen
└── README.md                         # Dokumentation
```

---

## 🗃️ Datenbank-Schema

### Kern-Entitäten

1. **Geografie**
   - `country` - Länder
   - `region` - Regionen
   - `municipality` - Gemeinden
   - `street` - Straßen

2. **Benutzerverwaltung**
   - `user_table` - Benutzer
   - `role` - Rollen
   - `user_role` - Benutzer-Rollen-Verknüpfung

3. **Infrastruktur**
   - `cabinet` - Schaltschränke
   - `circuit_group` - Leitungsgruppen (Abgänge)
   - `pole` - Masten
   - `light_point` - Leuchtstellen (POIs)

4. **Materialwirtschaft**
   - `material_catalog` - Materialkatalog
   - `lamp` - Leuchtmittel
   - `light_point_material` - Material-Verknüpfung
   - `cabinet_material` - Material-Verknüpfung

5. **Energie & Abrechnung**
   - `electric_meter` - Stromzähler
   - `meter_reading` - Zählerstände
   - `invoice` - Rechnungen

6. **Betrieb & Wartung**
   - `incident_type` - Störungs-Typen
   - `incident_status` - Störungs-Status
   - `incident` - Störungsmeldungen

7. **Projekte**
   - `project_type` - Projekt-Typen
   - `project_status` - Projekt-Status
   - `project` - Projekte
   - `project_infrastructure` - Projekt-Infrastruktur-Verknüpfung

8. **Dokumentenmanagement**
   - `document_type` - Dokumenten-Typen
   - `document` - Dokumente

9. **Audit-Log**
   - `audit_log` - Änderungen-Protokollierung

---

## 🎨 UI/UX-Design

### Farbschema (Dark Theme)

| Farbe | Hex-Code | Verwendung |
|-------|----------|------------|
| Hintergrund | `#1E1E1E` | Haupt-Hintergrund |
| Oberfläche | `#2D2D2D` | Karten, Tabellen |
| Primär (Orange) | `#FF8C00` | Aktive Elemente, Buttons |
| Sekundär (Orange) | `#FF6B35` | Hover-Effekte |
| Akzent (Orange) | `#FFA500` | Highlights |
| Text | `#E0E0E0` | Standard-Text |
| Text Sekundär | `#A0A0A0` | Deaktivierter Text |
| Rahmen | `#404040` | Rahmen, Trennlinien |
| Erfolg | `#4CAF50` | Erfolgmeldungen |
| Warnung | `#FF9800` | Warnungen |
| Fehler | `#F44336` | Fehlermeldungen |
| Info | `#2196F3` | Informationsmeldungen |

### Multi-Window-Workspace

- **Docking-System**: Flexible Anordnung von Fenstern
- **Tab-System**: Mehrere Ansichten in einem Fenster
- **Hauptbereiche**:
  - **Links**: Filter-Panel, Navigation
  - **Mitte**: Tabellenansichten, Detailansichten
  - **Rechts**: Kartenansicht, GIS-Layer

### GIS-Kartenansicht

- **Karten-Hintergrund**: OpenStreetMap oder Geoportail Luxembourg
- **Layer-Steuerung**: Ein-/Ausblenden von:
  - Schaltschränke
  - Masten
  - Leuchtstellen
  - Leitungsgruppen
- **Interaktive Funktionen**:
  - Zoom, Pan
  - Feature-Auswahl
  - Popups mit Details

---

## 🔧 API-Endpunkte

### Basis-URL
```
http://localhost:8000/api/v1
```

### Authentifizierung
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/auth/token` | POST | Login, Token erhalten |
| `/auth/refresh` | POST | Token erneuern |
| `/auth/logout` | POST | Abmelden |
| `/auth/me` | GET | Aktueller Benutzer |

### Benutzerverwaltung
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/users` | GET | Alle Benutzer abrufen |
| `/users` | POST | Benutzer erstellen |
| `/users/{id}` | GET | Benutzer abrufen |
| `/users/{id}` | PUT | Benutzer aktualisieren |
| `/users/{id}` | DELETE | Benutzer löschen |
| `/users/roles` | GET | Alle Rollen abrufen |
| `/users/roles` | POST | Rolle erstellen |

### Geografie
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/geography/countries` | GET | Alle Länder abrufen |
| `/geography/countries` | POST | Land erstellen |
| `/geography/regions` | GET | Alle Regionen abrufen |
| `/geography/municipalities` | GET | Alle Gemeinden abrufen |
| `/geography/streets` | GET | Alle Straßen abrufen |

### Infrastruktur
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/cabinets` | GET | Alle Schaltschränke abrufen |
| `/cabinets` | POST | Schaltschrank erstellen |
| `/cabinets/{id}` | GET | Schaltschrank abrufen |
| `/cabinets/{id}` | PUT | Schaltschrank aktualisieren |
| `/cabinets/{id}` | DELETE | Schaltschrank löschen |
| `/circuit-groups` | GET | Alle Leitungsgruppen abrufen |
| `/poles` | GET | Alle Masten abrufen |
| `/light-points` | GET | Alle Leuchtstellen abrufen |
| `/light-points/gis` | GET | Leuchtstellen im GIS-Bereich |

### Materialwirtschaft
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/materials/catalog` | GET | Alle Materialien abrufen |
| `/materials/catalog` | POST | Material erstellen |
| `/lamps` | GET | Alle Leuchtmittel abrufen |
| `/lamps` | POST | Leuchtmittel erstellen |

### Energie & Abrechnung
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/meters` | GET | Alle Stromzähler abrufen |
| `/meters` | POST | Stromzähler erstellen |
| `/meters/{id}/readings` | GET | Zählerstände abrufen |
| `/meters/{id}/readings` | POST | Zählerstand erstellen |
| `/invoices` | GET | Alle Rechnungen abrufen |
| `/invoices` | POST | Rechnung erstellen |

### Wartung & Störungen
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/incidents/types` | GET | Alle Störungs-Typen abrufen |
| `/incidents/statuses` | GET | Alle Störungs-Status abrufen |
| `/incidents` | GET | Alle Störungsmeldungen abrufen |
| `/incidents` | POST | Störungsmeldung erstellen |
| `/incidents/{id}` | GET | Störungsmeldung abrufen |
| `/incidents/{id}/assign` | POST | Störung zuweisen |
| `/incidents/{id}/resolve` | POST | Störung als erledigt markieren |

### Projekte
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/projects/types` | GET | Alle Projekt-Typen abrufen |
| `/projects/statuses` | GET | Alle Projekt-Status abrufen |
| `/projects` | GET | Alle Projekte abrufen |
| `/projects` | POST | Projekt erstellen |
| `/projects/{id}` | GET | Projekt abrufen |
| `/projects/{id}/infrastructure` | GET | Projekt-Infrastruktur abrufen |
| `/projects/{id}/infrastructure` | POST | Infrastruktur-Element hinzufügen |

### Dokumente
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/documents/types` | GET | Alle Dokumenten-Typen abrufen |
| `/documents` | GET | Alle Dokumente abrufen |
| `/documents/upload` | POST | Dokument hochladen |
| `/documents/{id}/download` | GET | Dokument herunterladen |
| `/documents/{id}` | DELETE | Dokument löschen |

### Audit-Log
| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/audit` | GET | Audit-Log abrufen |
| `/audit/{id}` | GET | Audit-Log-Eintrag abrufen |
| `/audit/statistics` | GET | Audit-Log-Statistiken |

---

## 👥 Benutzerrollen

| Rolle | Berechtigungen |
|-------|----------------|
| **admin** | Vollzugriff auf alle Funktionen |
| **technician** | Wartung, Störungsmeldungen, Reparaturen |
| **clerk** | Verwaltung, Dokumentenmanagement |
| **viewer** | Nur Lesezugriff |

---

## 📊 Performance-Optimierungen

### Datenbank
- **Räumliche Indizes**: PostGIS GIST-Indizes für GIS-Abfragen
- **Partitionierung**: Tabellen nach Region/Zeit partitioniert
- **Connection Pooling**: Verbindungspool für hohe Concurrent-User-Zahlen
- **Caching**: Redis-Cache für häufige Abfragen

### API
- **Pagination**: Alle Listen-Endpunkte unterstützen Pagination
- **Lazy Loading**: Daten werden nur bei Bedarf geladen
- **Asynchrone Verarbeitung**: Celery für Hintergrundaufgaben

### Frontend
- **Virtuelles Scrolling**: Nur sichtbare Zeilen werden geladen
- **GIS-Optimierung**: Vector Tiles, Clustering, LOD
- **Multi-Threading**: Asynchrone API-Aufrufe

---

## 🔒 Sicherheit

### Authentifizierung
- **JWT-Tokens**: Sichere Token-basierte Authentifizierung
- **Token-Erneuerung**: Refresh-Tokens für langlebige Sessions
- **Passwort-Hashing**: BCrypt für sichere Passwortspeicherung

### Berechtigungen
- **Rollenbasierte Zugriffskontrolle (RBAC)**
- **Ressourcen-basierte Berechtigungen**

### Datenschutz
- **Audit-Log**: Alle Änderungen werden protokolliert
- **IP-Tracking**: IP-Adressen werden für Audit-Logs gespeichert

---

## 📝 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE) für Details.

---

## 🤝 Mitwirken

1. **Fork** das Repository
2. Erstelle einen **Feature-Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. **Push** zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen **Pull Request**

---

## 📞 Kontakt

- **Projektverantwortlicher**: Joe the Sailor
- **E-Mail**: joe@sailor.lu
- **GitHub**: https://github.com/joe-the-sailor

---

## 🙏 Danksagungen

- [FastAPI](https://fastapi.tiangolo.com/) - Web-Framework
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI-Framework
- [PostgreSQL](https://www.postgresql.org/) + [PostGIS](https://postgis.net/) - Datenbank
- [OpenStreetMap](https://www.openstreetmap.org/) - Kartendaten
- [Geoportail Luxembourg](https://map.geoportail.lu/) - Offizielle Kartendaten

---

*© 2024 Sailight - Administration des Ponts et Chaussées, Luxemburg*
