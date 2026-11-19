"""
Leitungsgruppen-Ansicht
Tabellenansicht für Leitungsgruppen
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
import logging

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.circuit_group_view")


class CircuitGroupView(QWidget):
    """Tabellenansicht für Leitungsgruppen"""
    
    def __init__(self, parent=None):
        """Initialisiert die Leitungsgruppen-Ansicht"""
        super().__init__(parent)
        
        self.setWindowTitle("Leitungsgruppen")
        self.setObjectName("CircuitGroupView")
        
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
        
        logger.info("Leitungsgruppen-Ansicht initialisiert")
    
    def _setup_columns(self):
        """Richtet die Spalten ein"""
        headers = [
            "ID", "Identifier", "Name", "Phase", 
            "Sicherung (A)", "Status", "Schaltschrank", "Leuchtstellen"
        ]
        self._model.setHorizontalHeaderLabels(headers)
        
        # Spaltenbreiten
        self._table_view.setColumnWidth(0, 50)
        self._table_view.setColumnWidth(1, 120)
        self._table_view.setColumnWidth(2, 150)
        self._table_view.setColumnWidth(3, 80)
        self._table_view.setColumnWidth(4, 100)
        self._table_view.setColumnWidth(5, 100)
        self._table_view.setColumnWidth(6, 120)
        self._table_view.setColumnWidth(7, 80)
    
    async def _load_data(self):
        """Lädt die Daten"""
        if not auth_manager.is_authenticated:
            return
        
        response = await api_client.get(
            f"{config.API_V1_STR}/circuit-groups",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._model.clear()
            self._setup_columns()
            
            for item in response.data.get("items", []):
                self._add_circuit_group(item)
            
            logger.info(f"{len(response.data.get('items', []))} Leitungsgruppen geladen")
    
    def _add_circuit_group(self, data: dict):
        """Fügt eine Leitungsgruppe zur Tabelle hinzu"""
        row = []
        
        row.append(QStandardItem(str(data.get("id", ""))))
        row.append(QStandardItem(data.get("identifier", "")))
        row.append(QStandardItem(data.get("name", "")))
        row.append(QStandardItem(data.get("phase", "") or ""))
        row.append(QStandardItem(str(data.get("fuse_rating", "")) or ""))
        row.append(QStandardItem(data.get("status", "")))
        row.append(QStandardItem(str(data.get("cabinet_id", "")) if data.get("cabinet_id") else ""))
        row.append(QStandardItem(str(data.get("light_point_count", 0))))
        
        self._model.appendRow(row)
