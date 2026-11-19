"""
Login-Dialog für die Sailight-Anwendung
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import logging

from frontend.src.config import config
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.login_dialog")


class LoginDialog(QDialog):
    """Dialog für die Benutzeranmeldung"""
    
    # Signale
    login_success = pyqtSignal()
    login_failed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialisiert den Login-Dialog"""
        super().__init__(parent)
        
        # Fenster-Eigenschaften
        self.setWindowTitle("Anmelden - Sailight")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Hauptlayout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(15)
        
        # Titel
        self._title_label = QLabel("Sailight", self)
        self._title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title_label.setStyleSheet(f"color: {config.PRIMARY_COLOR};")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._title_label)
        
        # Untertitel
        self._subtitle_label = QLabel("Straßenbeleuchtungsverwaltung", self)
        self._subtitle_label.setFont(QFont("Segoe UI", 12))
        self._subtitle_label.setStyleSheet(f"color: {config.TEXT_SECONDARY};")
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._subtitle_label)
        
        # Formular
        self._form_layout = QFormLayout()
        self._form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self._form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addLayout(self._form_layout)
        
        # Benutzername
        self._username_label = QLabel("Benutzername:", self)
        self._username_input = QLineEdit(self)
        self._username_input.setPlaceholderText("Benutzername eingeben")
        self._username_input.setFocus()
        self._form_layout.addRow(self._username_label, self._username_input)
        
        # Passwort
        self._password_label = QLabel("Passwort:", self)
        self._password_input = QLineEdit(self)
        self._password_input.setPlaceholderText("Passwort eingeben")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._form_layout.addRow(self._password_label, self._password_input)
        
        # Button-Layout
        self._button_layout = QHBoxLayout()
        self._button_layout.setSpacing(10)
        self._main_layout.addLayout(self._button_layout)
        
        # Abbrechen-Button
        self._cancel_button = QPushButton("Abbrechen", self)
        self._cancel_button.setFixedWidth(100)
        self._cancel_button.clicked.connect(self.reject)
        self._button_layout.addWidget(self._cancel_button)
        
        # Anmelden-Button
        self._login_button = QPushButton("Anmelden", self)
        self._login_button.setFixedWidth(100)
        self._login_button.setProperty("primary", True)
        self._login_button.clicked.connect(self._on_login_clicked)
        self._button_layout.addWidget(self._login_button)
        
        # Fehler-Meldung
        self._error_label = QLabel(self)
        self._error_label.setStyleSheet(f"color: {config.ERROR_COLOR}; font-size: 12px;")
        self._error_label.setVisible(False)
        self._main_layout.addWidget(self._error_label)
        
        # Auth-Manager Signale verbinden
        auth_manager.login_success.connect(self._on_login_success)
        auth_manager.login_failed.connect(self._on_login_failed)
        
        # Enter-Taste verbinden
        self._username_input.returnPressed.connect(self._password_input.setFocus)
        self._password_input.returnPressed.connect(self._on_login_clicked)
        
        logger.info("Login-Dialog initialisiert")
    
    def _on_login_clicked(self):
        """Wird aufgerufen, wenn der Login-Button geklickt wird"""
        username = self._username_input.text().strip()
        password = self._password_input.text()
        
        # Validierung
        if not username:
            self._show_error("Bitte geben Sie einen Benutzernamen ein")
            self._username_input.setFocus()
            return
        
        if not password:
            self._show_error("Bitte geben Sie ein Passwort ein")
            self._password_input.setFocus()
            return
        
        # Login durchführen
        self._login_button.setEnabled(False)
        self._login_button.setText("Anmeldung...")
        self._error_label.setVisible(False)
        
        import asyncio
        async def do_login():
            await auth_manager.login(username, password)
        
        # In einem separaten Thread ausführen
        from PyQt6.QtCore import QThread, QObject, pyqtSignal
        
        class LoginWorker(QObject):
            finished = pyqtSignal()
            
            def __init__(self):
                super().__init__()
                self.username = username
                self.password = password
            
            def run(self):
                import asyncio
                asyncio.run(auth_manager.login(self.username, self.password))
                self.finished.emit()
        
        worker = LoginWorker()
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        
        # Signal verbinden, um Button wieder zu aktivieren
        auth_manager.login_success.connect(lambda: self._on_login_complete(True))
        auth_manager.login_failed.connect(lambda: self._on_login_complete(False))
    
    def _on_login_success(self, user):
        """Wird aufgerufen, wenn die Anmeldung erfolgreich war"""
        self._on_login_complete(True)
    
    def _on_login_failed(self, error: str):
        """Wird aufgerufen, wenn die Anmeldung fehlgeschlagen ist"""
        self._show_error(error)
        self._on_login_complete(False)
    
    def _on_login_complete(self, success: bool):
        """Wird aufgerufen, wenn der Login-Vorgang abgeschlossen ist"""
        self._login_button.setEnabled(True)
        self._login_button.setText("Anmelden")
        
        if success:
            self.accept()
            self.login_success.emit()
    
    def _show_error(self, message: str):
        """Zeigt eine Fehlermeldung an"""
        self._error_label.setText(message)
        self._error_label.setVisible(True)
        logger.warning(f"Login-Fehler: {message}")
    
    def clear(self):
        """Setzt das Formular zurück"""
        self._username_input.clear()
        self._password_input.clear()
        self._error_label.setVisible(False)
        self._username_input.setFocus()
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn der Dialog geschlossen wird"""
        self.clear()
        event.accept()
