"""
Detailansicht für ausgewählte Objekte
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import logging

from frontend.src.config import config

logger = logging.getLogger("sailight.detail_view")


class DetailView(QWidget):
    """Detailansicht für ausgewählte Objekte"""
    
    def __init__(self, parent=None):
        """Initialisiert die Detailansicht"""
        super().__init__(parent)
        
        self.setWindowTitle("Details")
        self.setObjectName("DetailView")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(10, 10, 10, 10)
        self._main_layout.setSpacing(10)
        
        # Titel
        self._title_label = QLabel("Objekt-Details", self)
        self._title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._title_label.setStyleSheet(f"color: {config.PRIMARY_COLOR};")
        self._main_layout.addWidget(self._title_label)
        
        # Tab-Widget für verschiedene Ansichten
        self._tab_widget = QTabWidget(self)
        self._main_layout.addWidget(self._tab_widget)
        
        # Allgemein-Tab
        self._general_tab = QWidget(self)
        self._general_layout = QVBoxLayout(self._general_tab)
        self._general_layout.setContentsMargins(10, 10, 10, 10)
        self._general_layout.setSpacing(10)
        
        self._general_text = QTextEdit(self._general_tab)
        self._general_text.setReadOnly(True)
        self._general_text.setStyleSheet(f"background-color: {config.BACKGROUND_COLOR}; color: {config.TEXT_COLOR}; border: 1px solid {config.BORDER_COLOR}; border-radius: 4px;")
        self._general_layout.addWidget(self._general_text)
        
        self._tab_widget.addTab(self._general_tab, "Allgemein")
        
        # Technische Daten-Tab
        self._technical_tab = QWidget(self)
        self._technical_layout = QVBoxLayout(self._technical_tab)
        self._technical_layout.setContentsMargins(10, 10, 10, 10)
        self._technical_layout.setSpacing(10)
        
        self._technical_text = QTextEdit(self._technical_tab)
        self._technical_text.setReadOnly(True)
        self._technical_text.setStyleSheet(f"background-color: {config.BACKGROUND_COLOR}; color: {config.TEXT_COLOR}; border: 1px solid {config.BORDER_COLOR}; border-radius: 4px;")
        self._technical_layout.addWidget(self._technical_text)
        
        self._tab_widget.addTab(self._technical_tab, "Technische Daten")
        
        # Dokumente-Tab
        self._documents_tab = QWidget(self)
        self._documents_layout = QVBoxLayout(self._documents_tab)
        self._documents_layout.setContentsMargins(10, 10, 10, 10)
        self._documents_layout.setSpacing(10)
        
        self._documents_label = QLabel("Keine Dokumente verfügbar", self._documents_tab)
        self._documents_label.setStyleSheet(f"color: {config.TEXT_SECONDARY};")
        self._documents_layout.addWidget(self._documents_label)
        self._documents_layout.addStretch()
        
        self._tab_widget.addTab(self._documents_tab, "Dokumente")
        
        # Historie-Tab
        self._history_tab = QWidget(self)
        self._history_layout = QVBoxLayout(self._history_tab)
        self._history_layout.setContentsMargins(10, 10, 10, 10)
        self._history_layout.setSpacing(10)
        
        self._history_text = QTextEdit(self._history_tab)
        self._history_text.setReadOnly(True)
        self._history_text.setStyleSheet(f"background-color: {config.BACKGROUND_COLOR}; color: {config.TEXT_COLOR}; border: 1px solid {config.BORDER_COLOR}; border-radius: 4px;")
        self._history_layout.addWidget(self._history_text)
        
        self._tab_widget.addTab(self._history_tab, "Historie")
        
        logger.info("Detailansicht initialisiert")
    
    def set_object(self, obj_type: str, data: dict):
        """Setzt das anzuzeigende Objekt"""
        self._title_label.setText(f"{obj_type.replace('_', ' ').title()} - Details")
        
        # Allgemeine Informationen
        general_info = self._format_general_info(obj_type, data)
        self._general_text.setPlainText(general_info)
        
        # Technische Informationen
        technical_info = self._format_technical_info(obj_type, data)
        self._technical_text.setPlainText(technical_info)
        
        # Historie (leer für jetzt)
        self._history_text.setPlainText("Keine Historie verfügbar")
    
    def _format_general_info(self, obj_type: str, data: dict) -> str:
        """Formatiert die allgemeinen Informationen"""
        lines = []
        lines.append(f"Typ: {obj_type.replace('_', ' ').title()}")
        lines.append(f"ID: {data.get('id', 'N/A')}")
        lines.append(f"UUID: {data.get('uuid', 'N/A')}")
        
        if "identifier" in data:
            lines.append(f"Identifier: {data['identifier']}")
        
        if "name" in data:
            lines.append(f"Name: {data['name']}")
        
        if "status" in data:
            lines.append(f"Status: {data['status']}")
        
        if "created_at" in data:
            lines.append(f"Erstellt: {data['created_at']}")
        
        if "updated_at" in data:
            lines.append(f"Aktualisiert: {data['updated_at']}")
        
        if "notes" in data and data["notes"]:
            lines.append(f"\nNotizen:\n{data['notes']}")
        
        return "\n".join(lines)
    
    def _format_technical_info(self, obj_type: str, data: dict) -> str:
        """Formatiert die technischen Informationen"""
        lines = []
        
        if obj_type == "cabinet":
            if "voltage_level" in data:
                lines.append(f"Spannungsebene: {data['voltage_level']}")
            if "installation_date" in data:
                lines.append(f"Installationsdatum: {data['installation_date']}")
            if "responsible_user_id" in data:
                lines.append(f"Verantwortlicher: {data['responsible_user_id']}")
            lines.append(f"Leitungsgruppen: {data.get('circuit_group_count', 0)}")
            lines.append(f"Leuchtstellen: {data.get('light_point_count', 0)}")
        
        elif obj_type == "light_point":
            if "power" in data:
                lines.append(f"Leistung: {data['power']} W")
            if "light_type" in data:
                lines.append(f"Leuchtentyp: {data['light_type']}")
            if "mounting_height" in data:
                lines.append(f"Montagehöhe: {data['mounting_height']} m")
            if "orientation" in data:
                lines.append(f"Ausrichtung: {data['orientation']}")
            if "installation_date" in data:
                lines.append(f"Installationsdatum: {data['installation_date']}")
            if "last_maintenance_date" in data:
                lines.append(f"Letzte Wartung: {data['last_maintenance_date']}")
            if "next_maintenance_date" in data:
                lines.append(f"Nächste Wartung: {data['next_maintenance_date']}")
        
        elif obj_type == "pole":
            if "height" in data:
                lines.append(f"Höhe: {data['height']} m")
            if "material" in data:
                lines.append(f"Material: {data['material']}")
            if "type_id" in data:
                lines.append(f"Typ: {data['type_id']}")
            if "installation_date" in data:
                lines.append(f"Installationsdatum: {data['installation_date']}")
            if "owner" in data:
                lines.append(f"Eigentümer: {data['owner']}")
        
        elif obj_type == "circuit_group":
            if "phase" in data:
                lines.append(f"Phase: {data['phase']}")
            if "fuse_rating" in data:
                lines.append(f"Sicherung: {data['fuse_rating']} A")
            if "cable_type_id" in data:
                lines.append(f"Kabeltyp: {data['cable_type_id']}")
            if "cable_length" in data:
                lines.append(f"Kabellänge: {data['cable_length']} m")
            if "installation_date" in data:
                lines.append(f"Installationsdatum: {data['installation_date']}")
            lines.append(f"Leuchtstellen: {data.get('light_point_count', 0)}")
        
        if not lines:
            lines.append("Keine technischen Informationen verfügbar")
        
        return "\n".join(lines)
