"""
Dashboard-Ansicht für die Sailight-Anwendung
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QGroupBox, QFrame
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, Any
import logging

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.dashboard")


class DashboardView(QWidget):
    """Dashboard-Ansicht mit Übersichtsdaten"""
    
    def __init__(self, parent=None):
        """Initialisiert das Dashboard"""
        super().__init__(parent)
        
        # Fenster-Eigenschaften
        self.setWindowTitle("Dashboard")
        self.setObjectName("DashboardView")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(10, 10, 10, 10)
        self._main_layout.setSpacing(10)
        
        # Überschrift
        self._create_header()
        
        # Statistik-Karten
        self._create_statistics_cards()
        
        # Schnellzugriff
        self._create_quick_access()
        
        # Daten laden
        self._load_data()
        
        logger.info("Dashboard initialisiert")
    
    def _create_header(self):
        """Erstellt die Überschrift"""
        header_label = QLabel("Dashboard", self)
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {config.PRIMARY_COLOR};")
        header_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._main_layout.addWidget(header_label)
        
        # Untertitel
        subtitle_label = QLabel("Übersicht über die Straßenbeleuchtungs-Infrastruktur", self)
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet(f"color: {config.TEXT_SECONDARY};")
        self._main_layout.addWidget(subtitle_label)
    
    def _create_statistics_cards(self):
        """Erstellt die Statistik-Karten"""
        stats_group = QGroupBox("Statistiken", self)
        stats_layout = QGridLayout(stats_group)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        stats_layout.setSpacing(15)
        
        # Schaltschränke
        self._cabinets_card = self._create_stat_card(
            "Schaltschränke",
            "0",
            "server",
            config.PRIMARY_COLOR
        )
        stats_layout.addWidget(self._cabinets_card, 0, 0)
        
        # Leitungsgruppen
        self._circuit_groups_card = self._create_stat_card(
            "Leitungsgruppen",
            "0",
            "network-server",
            config.SECONDARY_COLOR
        )
        stats_layout.addWidget(self._circuit_groups_card, 0, 1)
        
        # Masten
        self._poles_card = self._create_stat_card(
            "Masten",
            "0",
            "flag",
            config.ACCENT_COLOR
        )
        stats_layout.addWidget(self._poles_card, 0, 2)
        
        # Leuchtstellen
        self._light_points_card = self._create_stat_card(
            "Leuchtstellen",
            "0",
            "lightbulb",
            config.WARNING_COLOR
        )
        stats_layout.addWidget(self._light_points_card, 0, 3)
        
        # Aktive Störungen
        self._active_incidents_card = self._create_stat_card(
            "Aktive Störungen",
            "0",
            "dialog-warning",
            config.ERROR_COLOR
        )
        stats_layout.addWidget(self._active_incidents_card, 1, 0)
        
        # Projekte
        self._projects_card = self._create_stat_card(
            "Projekte",
            "0",
            "folder",
            config.INFO_COLOR
        )
        stats_layout.addWidget(self._projects_card, 1, 1)
        
        # Stromzähler
        self._meters_card = self._create_stat_card(
            "Stromzähler",
            "0",
            "utilities-terminal",
            config.SUCCESS_COLOR
        )
        stats_layout.addWidget(self._meters_card, 1, 2)
        
        self._main_layout.addWidget(stats_group)
    
    def _create_stat_card(self, title: str, value: str, icon_name: str, color: str) -> QWidget:
        """Erstellt eine Statistik-Karte"""
        card = QFrame(self)
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"background-color: {config.SURFACE_COLOR}; border-radius: 8px; border: 1px solid {config.BORDER_COLOR};")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Icon
        icon_label = QLabel(card)
        icon_label.setPixmap(QIcon.fromTheme(icon_name).pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Wert
        value_label = QLabel(value, card)
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Titel
        title_label = QLabel(title, card)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet(f"color: {config.TEXT_SECONDARY};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        return card
    
    def _create_quick_access(self):
        """Erstellt den Schnellzugriffs-Bereich"""
        quick_access_group = QGroupBox("Schnellzugriff", self)
        quick_access_layout = QHBoxLayout(quick_access_group)
        quick_access_layout.setContentsMargins(10, 10, 10, 10)
        quick_access_layout.setSpacing(10)
        
        # Karte
        map_button = self._create_quick_access_button("Karte", "map", config.PRIMARY_COLOR)
        map_button.clicked.connect(self._show_map)
        quick_access_layout.addWidget(map_button)
        
        # Schaltschränke
        cabinets_button = self._create_quick_access_button("Schaltschränke", "server", config.SECONDARY_COLOR)
        cabinets_button.clicked.connect(self._show_cabinets)
        quick_access_layout.addWidget(cabinets_button)
        
        # Leuchtstellen
        light_points_button = self._create_quick_access_button("Leuchtstellen", "lightbulb", config.ACCENT_COLOR)
        light_points_button.clicked.connect(self._show_light_points)
        quick_access_layout.addWidget(light_points_button)
        
        # Störungen
        incidents_button = self._create_quick_access_button("Störungen", "dialog-warning", config.ERROR_COLOR)
        incidents_button.clicked.connect(self._show_incidents)
        quick_access_layout.addWidget(incidents_button)
        
        self._main_layout.addWidget(quick_access_group)
        self._main_layout.addStretch()
    
    def _create_quick_access_button(self, title: str, icon_name: str, color: str) -> QWidget:
        """Erstellt einen Schnellzugriffs-Button"""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton(title, self)
        button.setIcon(QIcon.fromTheme(icon_name))
        button.setIconSize(QSize(24, 24))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {config.BACKGROUND_COLOR};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """)
        button.setFixedSize(120, 60)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        return button
    
    async def _load_data(self):
        """Lädt die Daten für das Dashboard"""
        if not auth_manager.is_authenticated:
            return
        
        # Statistiken laden
        await self._load_statistics()
    
    async def _load_statistics(self):
        """Lädt die Statistiken"""
        # Schaltschränke
        response = await api_client.get(f"{config.API_V1_STR}/cabinets", params={"page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._cabinets_card.findChild(QLabel).setText(str(count))
        
        # Leitungsgruppen
        response = await api_client.get(f"{config.API_V1_STR}/circuit-groups", params={"page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._circuit_groups_card.findChild(QLabel).setText(str(count))
        
        # Masten
        response = await api_client.get(f"{config.API_V1_STR}/poles", params={"page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._poles_card.findChild(QLabel).setText(str(count))
        
        # Leuchtstellen
        response = await api_client.get(f"{config.API_V1_STR}/light-points", params={"page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._light_points_card.findChild(QLabel).setText(str(count))
        
        # Aktive Störungen
        response = await api_client.get(f"{config.API_V1_STR}/incidents", params={"is_open": True, "page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._active_incidents_card.findChild(QLabel).setText(str(count))
        
        # Projekte
        response = await api_client.get(f"{config.API_V1_STR}/projects", params={"page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._projects_card.findChild(QLabel).setText(str(count))
        
        # Stromzähler
        response = await api_client.get(f"{config.API_V1_STR}/meters", params={"page_size": 1})
        if response.success and response.data:
            count = response.data.get("total", 0)
            self._meters_card.findChild(QLabel).setText(str(count))
    
    def _show_map(self):
        """Zeigt die Kartenansicht an"""
        from PyQt6.QtCore import pyqtSignal
        self.parent().parent().view_changed.emit("map")
    
    def _show_cabinets(self):
        """Zeigt die Schaltschrank-Ansicht an"""
        self.parent().parent().view_changed.emit("cabinets")
    
    def _show_light_points(self):
        """Zeigt die Leuchtstellen-Ansicht an"""
        self.parent().parent().view_changed.emit("light_points")
    
    def _show_incidents(self):
        """Zeigt die Störungs-Ansicht an"""
        self.parent().parent().view_changed.emit("incidents")
