"""
Masten-Ansicht
Tabellenansicht für Masten
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
import logging

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.pole_view")


class PoleView(QWidget):
    """Tabellenansicht für Masten"""
    
    def __init__(self, parent=None):
        """Initialisiert die Masten-Ansicht"""
        super().__init__(parent)
        
        self.setWindowTitle("Masten")
        self.setObjectName("PoleView")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
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
        
        logger.info("Masten-Ansicht initialisiert")
    
    def _setup_columns(self):
        """Richtet die Spalten ein"""
        headers = [
            "ID", "Identifier", "Höhe (m)", "Material", 
            "Status", "Straße", "Installationsdatum"
        ]
        self._model.setHorizontalHeaderLabels(headers)
        
        # Spaltenbreiten
        self._table_view.setColumnWidth(0, 50)
        self._table_view.setColumnWidth(1, 120)
        self._table_view.setColumnWidth(2, 80)
        self._table_view.setColumnWidth(3, 100)
        self._table_view.setColumnWidth(4, 100)
        self._table_view.setColumnWidth(5, 150)
        self._table_view.setColumnWidth(6, 120)
    
    async def _load_data(self):
        """Lädt die Daten"""
        if not auth_manager.is_authenticated:
            return
        
        response = await api_client.get(
            f"{config.API_V1_STR}/poles",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._model.clear()
            self._setup_columns()
            
            for item in response.data.get("items", []):
                self._add_pole(item)
            
            logger.info(f"{len(response.data.get('items', []))} Masten geladen")
    
    def _add_pole(self, data: dict):
        """Fügt einen Mast zur Tabelle hinzu"""
        row = []
        
        row.append(QStandardItem(str(data.get("id", ""))))
        row.append(QStandardItem(data.get("identifier", "")))
        row.append(QStandardItem(str(data.get("height", "")) or ""))
        row.append(QStandardItem(data.get("material", "") or ""))
        row.append(QStandardItem(data.get("status", "")))
        row.append(QStandardItem(str(data.get("street_id", "")) if data.get("street_id") else ""))
        row.append(QStandardItem(data.get("installation_date", "") or ""))
        
        self._model.appendRow(row)
