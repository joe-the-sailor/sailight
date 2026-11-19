# Sailight - Straßenbeleuchtungsverwaltung Luxemburg

Eine GUI-Anwendung zur Verwaltung der öffentlichen Beleuchtung in Luxemburg.

## Funktionen

- **Übersicht**: Anzeige aller Straßenlaternen mit Such- und Filterfunktionen
- **Verwaltung**: Bearbeiten von Laternendaten
- **Steuerung**: Ausführen von Steuerungsbefehlen für einzelne Laternen oder Gruppen
- **Wartung**: Protokollierung von Wartungsarbeiten
- **Energie**: Erfassung und Analyse des Energieverbrauchs
- **Zeitpläne**: Verwaltung von Beleuchtungszeitplänen
- **Statistik**: Übersichtsstatistiken und Verteilungen

## Anforderungen

- Python 3.6+
- Tkinter (standardmäßig in Python enthalten)
- SQLite3 (standardmäßig in Python enthalten)

## Installation

```bash
# Klonen des Repositories
git clone https://github.com/joe-the-sailor/sailight.git
cd sailight

# Ausführen der Anwendung
python3 main.py
```

## Verwendung

1. Starten Sie die Anwendung mit `python3 main.py`
2. Die Anwendung zeigt eine GUI mit mehreren Tabs
3. Nutzen Sie die Menüleiste für zusätzliche Funktionen

## Datenbank

Die Anwendung verwendet eine SQLite-Datenbank (`sailight.db`), die automatisch erstellt wird.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
