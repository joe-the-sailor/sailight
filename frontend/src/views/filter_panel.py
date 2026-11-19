"""
Filter-Panel für die Kartenansicht
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QComboBox, QLineEdit, QPushButton, QCheckBox,
    QLabel, QScrollArea
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, Any, List
import logging

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.filter_panel")


class FilterPanel(QWidget):
    """Filter-Panel für die Kartenansicht"""
    
    # Signale
    filters_changed = pyqtSignal(dict)
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialisiert das Filter-Panel"""
        super().__init__(parent)
        
        # Fenster-Eigenschaften
        self.setWindowTitle("Filter & Suche")
        self.setObjectName("FilterPanel")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(10, 10, 10, 10)
        self._main_layout.setSpacing(10)
        
        # ScrollArea für lange Listen
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QScrollArea.FrameShape.NoFrame)
        self._main_layout.addWidget(self._scroll_area)
        
        # Scroll-Widget
        self._scroll_widget = QWidget()
        self._scroll_area.setWidget(self._scroll_widget)
        
        # Scroll-Layout
        self._scroll_layout = QVBoxLayout(self._scroll_widget)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(10)
        
        # Suchgruppe
        self._create_search_group()
        
        # Infrastruktur-Gruppe
        self._create_infrastructure_group()
        
        # Geografie-Gruppe
        self._create_geography_group()
        
        # Status-Gruppe
        self._create_status_group()
        
        # Button-Gruppe
        self._create_button_group()
        
        # Daten laden
        self._load_initial_data()
        
        logger.info("Filter-Panel initialisiert")
    
    def _create_search_group(self):
        """Erstellt die Suchgruppe"""
        group = QGroupBox("Suche", self._scroll_widget)
        group_layout = QVBoxLayout(group)
        
        # Suchfeld
        self._search_input = QLineEdit(group)
        self._search_input.setPlaceholderText("Suchbegriff eingeben...")
        self._search_input.returnPressed.connect(self._on_search)
        group_layout.addWidget(self._search_input)
        
        # Such-Button
        search_button = QPushButton("Suchen", group)
        search_button.setIcon(QIcon.fromTheme("search"))
        search_button.clicked.connect(self._on_search)
        group_layout.addWidget(search_button)
        
        self._scroll_layout.addWidget(group)
    
    def _create_infrastructure_group(self):
        """Erstellt die Infrastruktur-Gruppe"""
        group = QGroupBox("Infrastruktur", self._scroll_widget)
        group_layout = QFormLayout(group)
        
        # Schaltschränke
        self._cabinet_combo = QComboBox(group)
        self._cabinet_combo.setPlaceholderText("Alle Schaltschränke")
        self._cabinet_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Schaltschrank:", self._cabinet_combo)
        
        # Leitungsgruppen
        self._circuit_group_combo = QComboBox(group)
        self._circuit_group_combo.setPlaceholderText("Alle Leitungsgruppen")
        self._circuit_group_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Leitungsgruppe:", self._circuit_group_combo)
        
        # Masten
        self._pole_combo = QComboBox(group)
        self._pole_combo.setPlaceholderText("Alle Masten")
        self._pole_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Mast:", self._pole_combo)
        
        # Leuchtstellen
        self._light_point_combo = QComboBox(group)
        self._light_point_combo.setPlaceholderText("Alle Leuchtstellen")
        self._light_point_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Leuchtstelle:", self._light_point_combo)
        
        self._scroll_layout.addWidget(group)
    
    def _create_geography_group(self):
        """Erstellt die Geografie-Gruppe"""
        group = QGroupBox("Geografie", self._scroll_widget)
        group_layout = QFormLayout(group)
        
        # Land
        self._country_combo = QComboBox(group)
        self._country_combo.setPlaceholderText("Alle Länder")
        self._country_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Land:", self._country_combo)
        
        # Region
        self._region_combo = QComboBox(group)
        self._region_combo.setPlaceholderText("Alle Regionen")
        self._region_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Region:", self._region_combo)
        
        # Gemeinde
        self._municipality_combo = QComboBox(group)
        self._municipality_combo.setPlaceholderText("Alle Gemeinden")
        self._municipality_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Gemeinde:", self._municipality_combo)
        
        # Straße
        self._street_combo = QComboBox(group)
        self._street_combo.setPlaceholderText("Alle Straßen")
        self._street_combo.currentIndexChanged.connect(self._on_filters_changed)
        group_layout.addRow("Straße:", self._street_combo)
        
        self._scroll_layout.addWidget(group)
    
    def _create_status_group(self):
        """Erstellt die Status-Gruppe"""
        group = QGroupBox("Status", self._scroll_widget)
        group_layout = QVBoxLayout(group)
        
        # Status-Filter
        self._status_active_check = QCheckBox("Aktiv", group)
        self._status_active_check.setChecked(True)
        self._status_active_check.stateChanged.connect(self._on_filters_changed)
        group_layout.addWidget(self._status_active_check)
        
        self._status_inactive_check = QCheckBox("Inaktiv", group)
        self._status_inactive_check.setChecked(True)
        self._status_inactive_check.stateChanged.connect(self._on_filters_changed)
        group_layout.addWidget(self._status_inactive_check)
        
        self._status_maintenance_check = QCheckBox("Wartung", group)
        self._status_maintenance_check.setChecked(True)
        self._status_maintenance_check.stateChanged.connect(self._on_filters_changed)
        group_layout.addWidget(self._status_maintenance_check)
        
        self._status_faulty_check = QCheckBox("Defekt", group)
        self._status_faulty_check.setChecked(True)
        self._status_faulty_check.stateChanged.connect(self._on_filters_changed)
        group_layout.addWidget(self._status_faulty_check)
        
        self._scroll_layout.addWidget(group)
    
    def _create_button_group(self):
        """Erstellt die Button-Gruppe"""
        group = QGroupBox("Aktionen", self._scroll_widget)
        group_layout = QVBoxLayout(group)
        
        # Zurücksetzen-Button
        reset_button = QPushButton("Filter zurücksetzen", group)
        reset_button.setIcon(QIcon.fromTheme("view-refresh"))
        reset_button.clicked.connect(self._reset_filters)
        group_layout.addWidget(reset_button)
        
        # Anwenden-Button
        apply_button = QPushButton("Filter anwenden", group)
        apply_button.setIcon(QIcon.fromTheme("check"))
        apply_button.setProperty("primary", True)
        apply_button.clicked.connect(self._apply_filters)
        group_layout.addWidget(apply_button)
        
        self._scroll_layout.addWidget(group)
        self._scroll_layout.addStretch()
    
    async def _load_initial_data(self):
        """Lädt die anfänglichen Daten"""
        if not auth_manager.is_authenticated:
            return
        
        # Länder laden
        await self._load_countries()
        
        # Schaltschränke laden
        await self._load_cabinets()
        
        # Masten laden
        await self._load_poles()
        
        # Leuchtstellen laden
        await self._load_light_points()
    
    async def _load_countries(self):
        """Lädt die Länder von der API"""
        response = await api_client.get(f"{config.API_V1_STR}/geography/countries")
        
        if response.success and response.data:
            self._country_combo.clear()
            self._country_combo.addItem("Alle Länder", None)
            
            for country in response.data.get("items", []):
                self._country_combo.addItem(country.get("name", ""), country.get("id"))
    
    async def _load_cabinets(self):
        """Lädt die Schaltschränke von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/cabinets",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._cabinet_combo.clear()
            self._cabinet_combo.addItem("Alle Schaltschränke", None)
            
            for cabinet in response.data.get("items", []):
                self._cabinet_combo.addItem(
                    f"{cabinet.get('identifier', '')} - {cabinet.get('name', '')}",
                    cabinet.get("id")
                )
    
    async def _load_poles(self):
        """Lädt die Masten von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/poles",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._pole_combo.clear()
            self._pole_combo.addItem("Alle Masten", None)
            
            for pole in response.data.get("items", []):
                self._pole_combo.addItem(
                    f"{pole.get('identifier', '')}",
                    pole.get("id")
                )
    
    async def _load_light_points(self):
        """Lädt die Leuchtstellen von der API"""
        response = await api_client.get(
            f"{config.API_V1_STR}/light-points",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._light_point_combo.clear()
            self._light_point_combo.addItem("Alle Leuchtstellen", None)
            
            for lp in response.data.get("items", []):
                self._light_point_combo.addItem(
                    f"{lp.get('identifier', '')}",
                    lp.get("id")
                )
    
    def _on_search(self):
        """Wird aufgerufen, wenn die Suche ausgelöst wird"""
        search_text = self._search_input.text().strip()
        if search_text:
            self.search_requested.emit(search_text)
    
    def _on_filters_changed(self):
        """Wird aufgerufen, wenn sich ein Filter ändert"""
        self._apply_filters()
    
    def _apply_filters(self):
        """Wendet die aktuellen Filter an"""
        filters = {
            "search": self._search_input.text().strip(),
            "cabinet_id": self._cabinet_combo.currentData(),
            "pole_id": self._pole_combo.currentData(),
            "light_point_id": self._light_point_combo.currentData(),
            "country_id": self._country_combo.currentData(),
            "municipality_id": self._municipality_combo.currentData(),
            "street_id": self._street_combo.currentData(),
            "status": self._get_status_filter()
        }
        
        self.filters_changed.emit(filters)
    
    def _get_status_filter(self) -> List[str]:
        """Gibt die ausgewählten Status-Filter zurück"""
        status = []
        
        if self._status_active_check.isChecked():
            status.append("active")
        if self._status_inactive_check.isChecked():
            status.append("inactive")
        if self._status_maintenance_check.isChecked():
            status.append("maintenance")
        if self._status_faulty_check.isChecked():
            status.append("faulty")
        
        return status
    
    def _reset_filters(self):
        """Setzt alle Filter zurück"""
        self._search_input.clear()
        
        self._cabinet_combo.setCurrentIndex(0)
        self._circuit_group_combo.setCurrentIndex(0)
        self._pole_combo.setCurrentIndex(0)
        self._light_point_combo.setCurrentIndex(0)
        
        self._country_combo.setCurrentIndex(0)
        self._region_combo.setCurrentIndex(0)
        self._municipality_combo.setCurrentIndex(0)
        self._street_combo.setCurrentIndex(0)
        
        self._status_active_check.setChecked(True)
        self._status_inactive_check.setChecked(True)
        self._status_maintenance_check.setChecked(True)
        self._status_faulty_check.setChecked(True)
        
        # Filter anwenden
        self._apply_filters()
    
    def set_filters(self, filters: Dict[str, Any]):
        """Setzt die Filter basierend auf einem Dictionary"""
        if "search" in filters:
            self._search_input.setText(filters["search"] or "")
        
        if "cabinet_id" in filters:
            index = self._cabinet_combo.findData(filters["cabinet_id"])
            if index >= 0:
                self._cabinet_combo.setCurrentIndex(index)
        
        if "pole_id" in filters:
            index = self._pole_combo.findData(filters["pole_id"])
            if index >= 0:
                self._pole_combo.setCurrentIndex(index)
        
        if "light_point_id" in filters:
            index = self._light_point_combo.findData(filters["light_point_id"])
            if index >= 0:
                self._light_point_combo.setCurrentIndex(index)
        
        if "status" in filters:
            status = filters["status"]
            self._status_active_check.setChecked("active" in status)
            self._status_inactive_check.setChecked("inactive" in status)
            self._status_maintenance_check.setChecked("maintenance" in status)
            self._status_faulty_check.setChecked("faulty" in status)
