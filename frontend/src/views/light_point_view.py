"""
Leuchtstellen-Ansicht
Tabellenansicht für Leuchtstellen (POIs)
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QToolBar
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QSize
import logging

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.light_point_view")


class LightPointView(QWidget):
    """Tabellenansicht für Leuchtstellen"""
    
    def __init__(self, parent=None):
        """Initialisiert die Leuchtstellen-Ansicht"""
        super().__init__(parent)
        
        self.setWindowTitle("Leuchtstellen")
        self.setObjectName("LightPointView")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Toolbar
        self._toolbar = QToolBar(self)
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(QSize(20, 20))
        self._main_layout.addWidget(self._toolbar)
        
        # Tabellenansicht
        self._table_view = QTableView(self)
        self._table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._main_layout.addWidget(self._table_view)
        
        # Modell
        self._model = QStandardItemModel(self)
        self._table_view.setModel(self._model)
        
        # Spalten
        self._setup_columns()
        
        # Daten laden
        self._load_data()
        
        logger.info("Leuchtstellen-Ansicht initialisiert")
    
    def _setup_columns(self):
        """Richtet die Spalten ein"""
        headers = [
            "ID", "Identifier", "Status", "Leuchtentyp", 
            "Leistung (W)", "Mast", "Leitungsgruppe", "Installationsdatum"
        ]
        self._model.setHorizontalHeaderLabels(headers)
        
        # Spaltenbreiten
        self._table_view.setColumnWidth(0, 50)
        self._table_view.setColumnWidth(1, 120)
        self._table_view.setColumnWidth(2, 100)
        self._table_view.setColumnWidth(3, 120)
        self._table_view.setColumnWidth(4, 80)
        self._table_view.setColumnWidth(5, 100)
        self._table_view.setColumnWidth(6, 120)
        self._table_view.setColumnWidth(7, 120)
    
    async def _load_data(self):
        """Lädt die Daten"""
        if not auth_manager.is_authenticated:
            return
        
        response = await api_client.get(
            f"{config.API_V1_STR}/light-points",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._model.clear()
            self._setup_columns()
            
            for item in response.data.get("items", []):
                self._add_light_point(item)
            
            logger.info(f"{len(response.data.get('items', []))} Leuchtstellen geladen")
    
    def _add_light_point(self, data: dict):
        """Fügt eine Leuchtstelle zur Tabelle hinzu"""
        row = []
        
        row.append(QStandardItem(str(data.get("id", ""))))
        row.append(QStandardItem(data.get("identifier", "")))
        row.append(QStandardItem(data.get("status", "")))
        row.append(QStandardItem(data.get("light_type", "")))
        row.append(QStandardItem(str(data.get("power", ""))))
        row.append(QStandardItem(str(data.get("pole_id", "")) if data.get("pole_id") else ""))
        row.append(QStandardItem(str(data.get("circuit_group_id", "")) if data.get("circuit_group_id") else ""))
        row.append(QStandardItem(data.get("installation_date", "") or ""))
        
        self._model.appendRow(row)
