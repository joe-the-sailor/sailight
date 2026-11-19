"""
Statusleiste für die Sailight-Anwendung
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QDateTime
from typing import Optional, List
import logging

from frontend.src.config import config

logger = logging.getLogger("sailight.status_bar")


class StatusBar(QStatusBar):
    """Statusleiste mit verschiedenen Statusinformationen"""
    
    def __init__(self, parent):
        """Initialisiert die Statusleiste"""
        super().__init__(parent)
        
        # Standard-Eigenschaften
        self.setSizeGripEnabled(True)
        
        # Zeit-Label
        self._time_label = QLabel(self)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_label.setFont(QFont("Segoe UI", 9))
        self._time_label.setStyleSheet(f"color: {config.TEXT_SECONDARY};")
        self._time_label.setMinimumWidth(100)
        self.addPermanentWidget(self._time_label)
        
        # Auth-Status-Label
        self._auth_label = QLabel("Nicht angemeldet", self)
        self._auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._auth_label.setFont(QFont("Segoe UI", 9))
        self._auth_label.setStyleSheet(f"color: {config.WARNING_COLOR};")
        self._auth_label.setMinimumWidth(120)
        self.addPermanentWidget(self._auth_label)
        
        # Benutzer-Label
        self._user_label = QLabel("", self)
        self._user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._user_label.setFont(QFont("Segoe UI", 9))
        self._user_label.setStyleSheet(f"color: {config.TEXT_COLOR};")
        self._user_label.setMinimumWidth(150)
        self.addPermanentWidget(self._user_label)
        
        # Aktuelle Ansicht-Label
        self._view_label = QLabel("Dashboard", self)
        self._view_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._view_label.setFont(QFont("Segoe UI", 9))
        self._view_label.setStyleSheet(f"color: {config.TEXT_COLOR};")
        self.addWidget(self._view_label)
        
        # Timer für Zeitaktualisierung
        self._time_timer = QTimer(self)
        self._time_timer.timeout.connect(self.update_time)
        self._time_timer.start(1000)  # Alle 1 Sekunde
        
        # Zeit sofort aktualisieren
        self.update_time()
        
        logger.info("Statusleiste initialisiert")
    
    def update_time(self):
        """Aktualisiert die Zeit"""
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        current_date = QDateTime.currentDateTime().toString("dd.MM.yyyy")
        self._time_label.setText(f"{current_date} {current_time}")
    
    def set_auth_status(self, status: str):
        """Setzt den Authentifizierungsstatus"""
        self._auth_label.setText(status)
        
        # Farbe anpassen
        if status == "Angemeldet":
            self._auth_label.setStyleSheet(f"color: {config.SUCCESS_COLOR};")
        else:
            self._auth_label.setStyleSheet(f"color: {config.WARNING_COLOR};")
    
    def set_user_info(self, display_name: str, roles: List[str]):
        """Setzt die Benutzerinformationen"""
        if display_name:
            roles_text = f" ({', '.join(roles)})" if roles else ""
            self._user_label.setText(f"{display_name}{roles_text}")
        else:
            self._user_label.setText("")
    
    def set_current_view(self, view_name: str):
        """Setzt die aktuelle Ansicht"""
        view_text = view_name.replace("_", " ").title()
        self._view_label.setText(f"Aktuelle Ansicht: {view_text}")
    
    def show_message(self, message: str, duration: int = 3000):
        """Zeigt eine temporäre Nachricht an"""
        # Temporäres Label erstellen
        temp_label = QLabel(message, self)
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_label.setFont(QFont("Segoe UI", 9))
        temp_label.setStyleSheet(f"color: {config.INFO_COLOR};")
        
        # Vor dem Benutzer-Label einfügen
        self.insertWidget(self.indexOf(self._user_label) - 1, temp_label)
        
        # Timer zum Entfernen
        QTimer.singleShot(duration, lambda: self.removeWidget(temp_label))
    
    def show_progress(self, value: int, max_value: int = 100):
        """Zeigt einen Fortschrittsbalken an"""
        # Bestehenden Fortschrittsbalken entfernen
        for widget in self.findChildren(QProgressBar):
            self.removeWidget(widget)
            widget.deleteLater()
        
        # Neuen Fortschrittsbalken erstellen
        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, max_value)
        progress_bar.setValue(value)
        progress_bar.setTextVisible(True)
        progress_bar.setFixedWidth(150)
        
        # Vor dem Benutzer-Label einfügen
        self.insertWidget(self.indexOf(self._user_label) - 1, progress_bar)
        
        return progress_bar
    
    def hide_progress(self):
        """Versteckt den Fortschrittsbalken"""
        for widget in self.findChildren(QProgressBar):
            self.removeWidget(widget)
            widget.deleteLater()
