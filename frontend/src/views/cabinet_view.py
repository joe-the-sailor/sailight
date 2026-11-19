"""
Schaltschrank-Ansicht
Tabellenansicht für Schaltschränke
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QToolBar, QLabel, QMessageBox,
    QInputDialog
)
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from typing import Optional, Dict, Any, List
import logging

from frontend.src.config import config
from frontend.src.utils.api_client import api_client
from frontend.src.utils.auth import auth_manager
from frontend.src.models.cabinet import Cabinet

logger = logging.getLogger("sailight.cabinet_view")


class Cabinet:
    """Datenmodell für Schaltschränke"""
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", 0)
        self.uuid = data.get("uuid", "")
        self.name = data.get("name", "")
        self.identifier = data.get("identifier", "")
        self.status = data.get("status", "")
        self.voltage_level = data.get("voltage_level", "")
        self.installation_date = data.get("installation_date", "")
        self.responsible_user_id = data.get("responsible_user_id", 0)
        self.notes = data.get("notes", "")
        self.created_at = data.get("created_at", "")
        self.updated_at = data.get("updated_at", "")
        self.circuit_group_count = data.get("circuit_group_count", 0)
        self.light_point_count = data.get("light_point_count", 0)


class CabinetView(QWidget):
    """Tabellenansicht für Schaltschränke"""
    
    # Signale
    cabinet_selected = pyqtSignal(Cabinet)
    cabinet_created = pyqtSignal(Cabinet)
    cabinet_updated = pyqtSignal(Cabinet)
    cabinet_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialisiert die Schaltschrank-Ansicht"""
        super().__init__(parent)
        
        # Fenster-Eigenschaften
        self.setWindowTitle("Schaltschränke")
        self.setObjectName("CabinetView")
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Toolbar erstellen
        self._toolbar = self._create_toolbar()
        self._main_layout.addWidget(self._toolbar)
        
        # Tabellenansicht
        self._table_view = QTableView(self)
        self._table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table_view.doubleClicked.connect(self._on_table_double_clicked)
        self._main_layout.addWidget(self._table_view)
        
        # Modell erstellen
        self._model = QStandardItemModel(self)
        self._table_view.setModel(self._model)
        
        # Spalten definieren
        self._setup_table_columns()
        
        # Daten laden
        self._load_data()
        
        # Auswahl verbinden
        self._table_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        logger.info("Schaltschrank-Ansicht initialisiert")
    
    def _create_toolbar(self) -> QToolBar:
        """Erstellt die Toolbar"""
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(20, 20))
        
        # Neu
        new_action = QAction("Neu", self)
        new_action.setIcon(QIcon.fromTheme("document-new"))
        new_action.setToolTip("Neuen Schaltschrank erstellen")
        new_action.triggered.connect(self._create_cabinet)
        toolbar.addAction(new_action)
        
        # Bearbeiten
        edit_action = QAction("Bearbeiten", self)
        edit_action.setIcon(QIcon.fromTheme("document-edit"))
        edit_action.setToolTip("Schaltschrank bearbeiten")
        edit_action.triggered.connect(self._edit_cabinet)
        toolbar.addAction(edit_action)
        
        # Löschen
        delete_action = QAction("Löschen", self)
        delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        delete_action.setToolTip("Schaltschrank löschen")
        delete_action.triggered.connect(self._delete_cabinet)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # Aktualisieren
        refresh_action = QAction("Aktualisieren", self)
        refresh_action.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_action.setToolTip("Daten aktualisieren")
        refresh_action.triggered.connect(self._load_data)
        toolbar.addAction(refresh_action)
        
        return toolbar
    
    def _setup_table_columns(self):
        """Richtet die Tabellenspalten ein"""
        # Spaltenüberschriften
        headers = [
            "ID", "Identifier", "Name", "Status", 
            "Spannung", "Leitungsgruppen", "Leuchtstellen", "Verantwortlich"
        ]
        
        self._model.setHorizontalHeaderLabels(headers)
        
        # Spaltenbreiten
        self._table_view.setColumnWidth(0, 50)  # ID
        self._table_view.setColumnWidth(1, 120)  # Identifier
        self._table_view.setColumnWidth(2, 150)  # Name
        self._table_view.setColumnWidth(3, 100)  # Status
        self._table_view.setColumnWidth(4, 100)  # Spannung
        self._table_view.setColumnWidth(5, 100)  # Leitungsgruppen
        self._table_view.setColumnWidth(6, 100)  # Leuchtstellen
        self._table_view.setColumnWidth(7, 150)  # Verantwortlich
    
    async def _load_data(self):
        """Lädt die Daten von der API"""
        if not auth_manager.is_authenticated:
            return
        
        response = await api_client.get(
            f"{config.API_V1_STR}/cabinets",
            params={"page_size": 10000}
        )
        
        if response.success and response.data:
            self._model.clear()
            self._setup_table_columns()
            
            for item in response.data.get("items", []):
                cabinet = Cabinet(item)
                self._add_cabinet_to_table(cabinet)
            
            logger.info(f"{len(response.data.get('items', []))} Schaltschränke geladen")
        else:
            logger.error(f"Fehler beim Laden der Schaltschränke: {response.error}")
    
    def _add_cabinet_to_table(self, cabinet: Cabinet):
        """Fügt einen Schaltschrank zur Tabelle hinzu"""
        row = []
        
        # ID
        row.append(QStandardItem(str(cabinet.id)))
        row[-1].setEditable(False)
        
        # Identifier
        row.append(QStandardItem(cabinet.identifier))
        row[-1].setEditable(False)
        
        # Name
        row.append(QStandardItem(cabinet.name))
        row[-1].setEditable(False)
        
        # Status
        status_item = QStandardItem(cabinet.status)
        if cabinet.status == "active":
            status_item.setBackground(QColor(config.SUCCESS_COLOR))
        elif cabinet.status == "inactive":
            status_item.setBackground(QColor(config.TEXT_SECONDARY))
        elif cabinet.status == "maintenance":
            status_item.setBackground(QColor(config.WARNING_COLOR))
        elif cabinet.status == "faulty":
            status_item.setBackground(QColor(config.ERROR_COLOR))
        row.append(status_item)
        row[-1].setEditable(False)
        
        # Spannung
        row.append(QStandardItem(cabinet.voltage_level or ""))
        row[-1].setEditable(False)
        
        # Leitungsgruppen
        row.append(QStandardItem(str(cabinet.circuit_group_count)))
        row[-1].setEditable(False)
        row[-1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Leuchtstellen
        row.append(QStandardItem(str(cabinet.light_point_count)))
        row[-1].setEditable(False)
        row[-1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Verantwortlich
        row.append(QStandardItem(str(cabinet.responsible_user_id) if cabinet.responsible_user_id else ""))
        row[-1].setEditable(False)
        
        self._model.appendRow(row)
    
    def _on_selection_changed(self):
        """Wird aufgerufen, wenn die Auswahl geändert wird"""
        indexes = self._table_view.selectionModel().selectedRows()
        
        if indexes:
            row = indexes[0].row()
            cabinet_id = int(self._model.item(row, 0).text())
            cabinet_name = self._model.item(row, 2).text()
            cabinet_identifier = self._model.item(row, 1).text()
            
            # Signal auslösen
            cabinet = Cabinet({
                "id": cabinet_id,
                "identifier": cabinet_identifier,
                "name": cabinet_name
            })
            self.cabinet_selected.emit(cabinet)
    
    def _on_table_double_clicked(self, index):
        """Wird aufgerufen, wenn auf eine Zeile doppelgeklickt wird"""
        self._edit_cabinet()
    
    def _create_cabinet(self):
        """Erstellt einen neuen Schaltschrank"""
        if not auth_manager.is_authenticated:
            QMessageBox.warning(self, "Fehler", "Bitte melden Sie sich an, um Schaltschränke zu erstellen")
            return
        
        # Dialog für neue Schaltschränke
        dialog = CabinetDialog(self, mode="create")
        if dialog.exec() == QMessageBox.StandardButton.Ok:
            cabinet_data = dialog.get_data()
            self._save_cabinet(cabinet_data)
    
    def _edit_cabinet(self):
        """Bearbeitet einen bestehenden Schaltschrank"""
        indexes = self._table_view.selectionModel().selectedRows()
        
        if not indexes:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen Schaltschrank aus")
            return
        
        if not auth_manager.is_authenticated:
            QMessageBox.warning(self, "Fehler", "Bitte melden Sie sich an, um Schaltschränke zu bearbeiten")
            return
        
        row = indexes[0].row()
        cabinet_id = int(self._model.item(row, 0).text())
        
        # Dialog für Bearbeitung
        dialog = CabinetDialog(self, mode="edit", cabinet_id=cabinet_id)
        if dialog.exec() == QMessageBox.StandardButton.Ok:
            cabinet_data = dialog.get_data()
            self._save_cabinet(cabinet_data)
    
    async def _save_cabinet(self, cabinet_data: Dict[str, Any]):
        """Speichert einen Schaltschrank"""
        if cabinet_data.get("id"):
            # Aktualisieren
            response = await api_client.put(
                f"{config.API_V1_STR}/cabinets/{cabinet_data['id']}",
                json=cabinet_data
            )
            if response.success:
                QMessageBox.information(self, "Erfolg", "Schaltschrank erfolgreich aktualisiert")
                self._load_data()
            else:
                QMessageBox.error(self, "Fehler", f"Fehler beim Aktualisieren: {response.error}")
        else:
            # Erstellen
            response = await api_client.post(
                f"{config.API_V1_STR}/cabinets",
                json=cabinet_data
            )
            if response.success:
                QMessageBox.information(self, "Erfolg", "Schaltschrank erfolgreich erstellt")
                self._load_data()
            else:
                QMessageBox.error(self, "Fehler", f"Fehler beim Erstellen: {response.error}")
    
    def _delete_cabinet(self):
        """Löscht einen Schaltschrank"""
        indexes = self._table_view.selectionModel().selectedRows()
        
        if not indexes:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen Schaltschrank aus")
            return
        
        if not auth_manager.is_authenticated:
            QMessageBox.warning(self, "Fehler", "Bitte melden Sie sich an, um Schaltschränke zu löschen")
            return
        
        row = indexes[0].row()
        cabinet_id = int(self._model.item(row, 0).text())
        cabinet_identifier = self._model.item(row, 1).text()
        
        # Bestätigung
        result = QMessageBox.question(
            self,
            "Löschen",
            f"Möchten Sie den Schaltschrank '{cabinet_identifier}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            import asyncio
            async def do_delete():
                response = await api_client.delete(f"{config.API_V1_STR}/cabinets/{cabinet_id}")
                if response.success:
                    QMessageBox.information(self, "Erfolg", "Schaltschrank erfolgreich gelöscht")
                    self._load_data()
                else:
                    QMessageBox.error(self, "Fehler", f"Fehler beim Löschen: {response.error}")
            
            asyncio.run(do_delete())


class CabinetDialog(QMessageBox):
    """Dialog für die Bearbeitung von Schaltschränken"""
    
    def __init__(self, parent=None, mode: str = "create", cabinet_id: Optional[int] = None):
        """Initialisiert den Dialog"""
        super().__init__(parent)
        
        self._mode = mode
        self._cabinet_id = cabinet_id
        self._data = {}
        
        # Dialog-Eigenschaften
        if mode == "create":
            self.setWindowTitle("Neuer Schaltschrank")
        else:
            self.setWindowTitle("Schaltschrank bearbeiten")
        
        self.setIcon(QMessageBox.Icon.NoIcon)
        self.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        # Layout
        self._layout = QVBoxLayout(self)
        
        # Formular erstellen
        self._create_form()
        
        # Daten laden (falls Bearbeitungsmodus)
        if mode == "edit" and cabinet_id:
            self._load_cabinet_data(cabinet_id)
    
    def _create_form(self):
        """Erstellt das Formular"""
        from PyQt6.QtWidgets import QFormLayout, QLineEdit, QComboBox
        
        form_layout = QFormLayout()
        
        # Identifier
        self._identifier_input = QLineEdit(self)
        form_layout.addRow("Identifier:", self._identifier_input)
        
        # Name
        self._name_input = QLineEdit(self)
        form_layout.addRow("Name:", self._name_input)
        
        # Status
        self._status_combo = QComboBox(self)
        self._status_combo.addItems(["active", "inactive", "maintenance", "faulty"])
        form_layout.addRow("Status:", self._status_combo)
        
        # Spannungsebene
        self._voltage_input = QLineEdit(self)
        form_layout.addRow("Spannungsebene:", self._voltage_input)
        
        # Notizen
        from PyQt6.QtWidgets import QTextEdit
        self._notes_input = QTextEdit(self)
        form_layout.addRow("Notizen:", self._notes_input)
        
        self._layout.addLayout(form_layout)
    
    async def _load_cabinet_data(self, cabinet_id: int):
        """Lädt die Daten eines Schaltschranks"""
        response = await api_client.get(f"{config.API_V1_STR}/cabinets/{cabinet_id}")
        
        if response.success and response.data:
            cabinet = response.data
            self._identifier_input.setText(cabinet.get("identifier", ""))
            self._name_input.setText(cabinet.get("name", ""))
            self._status_combo.setCurrentText(cabinet.get("status", "active"))
            self._voltage_input.setText(cabinet.get("voltage_level", ""))
            self._notes_input.setText(cabinet.get("notes", ""))
            
            self._data = cabinet
    
    def get_data(self) -> Dict[str, Any]:
        """Gibt die eingegebenen Daten zurück"""
        data = {
            "identifier": self._identifier_input.text().strip(),
            "name": self._name_input.text().strip(),
            "status": self._status_combo.currentText(),
            "voltage_level": self._voltage_input.text().strip(),
            "notes": self._notes_input.toPlainText().strip()
        }
        
        if self._mode == "edit" and self._cabinet_id:
            data["id"] = self._cabinet_id
        
        return data
