"""
Toolbar für die Sailight-Anwendung
"""

from PyQt6.QtWidgets import QToolBar, QToolButton, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal
import logging

from frontend.src.config import config
from frontend.src.utils.auth import auth_manager

logger = logging.getLogger("sailight.toolbar")


class ToolBar(QToolBar):
    """Toolbar mit Schnellzugriffs-Buttons"""
    
    # Signale
    view_requested = pyqtSignal(str)
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent: QWidget):
        """Initialisiert die Toolbar"""
        super().__init__(parent)
        
        # Toolbar-Eigenschaften
        self.setObjectName("MainToolBar")
        self.setMovable(True)
        self.setFloatable(True)
        self.setIconSize(QIcon.fromTheme("icon-size").actualSize(QSize(24, 24)))
        
        # Aktionen erstellen
        self._create_actions()
        
        # Toolbar befüllen
        self._setup_toolbar()
        
        # Auth-Manager Signale verbinden
        auth_manager.auth_state_changed.connect(self._on_auth_state_changed)
        
        logger.info("Toolbar initialisiert")
    
    def _create_actions(self):
        """Erstellt die Aktionen"""
        # Dashboard
        self._dashboard_action = QAction("Dashboard", self)
        self._dashboard_action.setIcon(QIcon.fromTheme("home"))
        self._dashboard_action.setToolTip("Dashboard anzeigen")
        self._dashboard_action.triggered.connect(lambda: self.view_requested.emit("dashboard"))
        
        # Karte
        self._map_action = QAction("Karte", self)
        self._map_action.setIcon(QIcon.fromTheme("map"))
        self._map_action.setToolTip("Karte anzeigen")
        self._map_action.triggered.connect(lambda: self.view_requested.emit("map"))
        
        # Schaltschränke
        self._cabinets_action = QAction("Schaltschränke", self)
        self._cabinets_action.setIcon(QIcon.fromTheme("server"))
        self._cabinets_action.setToolTip("Schaltschränke verwalten")
        self._cabinets_action.triggered.connect(lambda: self.view_requested.emit("cabinets"))
        
        # Leuchtstellen
        self._light_points_action = QAction("Leuchtstellen", self)
        self._light_points_action.setIcon(QIcon.fromTheme("lightbulb"))
        self._light_points_action.setToolTip("Leuchtstellen verwalten")
        self._light_points_action.triggered.connect(lambda: self.view_requested.emit("light_points"))
        
        # Masten
        self._poles_action = QAction("Masten", self)
        self._poles_action.setIcon(QIcon.fromTheme("flag"))
        self._poles_action.setToolTip("Masten verwalten")
        self._poles_action.triggered.connect(lambda: self.view_requested.emit("poles"))
        
        # Leitungsgruppen
        self._circuit_groups_action = QAction("Leitungsgruppen", self)
        self._circuit_groups_action.setIcon(QIcon.fromTheme("network-server"))
        self._circuit_groups_action.setToolTip("Leitungsgruppen verwalten")
        self._circuit_groups_action.triggered.connect(lambda: self.view_requested.emit("circuit_groups"))
        
        # Separator
        self._separator1 = self.addSeparator()
        
        # Suchfeld
        self._search_action = QAction("Suche", self)
        self._search_action.setIcon(QIcon.fromTheme("search"))
        self._search_action.setToolTip("Suche")
        
        # Benutzer
        self._user_action = QAction("Benutzer", self)
        self._user_action.setIcon(QIcon.fromTheme("user"))
        self._user_action.setToolTip("Benutzerinformationen")
        self._user_action.triggered.connect(self._show_user_menu)
    
    def _setup_toolbar(self):
        """Richtet die Toolbar ein"""
        # Standard-Aktionen hinzufügen
        self.addAction(self._dashboard_action)
        self.addAction(self._map_action)
        self.addSeparator()
        self.addAction(self._cabinets_action)
        self.addAction(self._light_points_action)
        self.addAction(self._poles_action)
        self.addAction(self._circuit_groups_action)
        self.addSeparator()
        
        # Suchfeld
        self._search_widget = self._create_search_widget()
        self.addWidget(self._search_widget)
        
        # Benutzer
        self.addSeparator()
        self.addAction(self._user_action)
    
    def _create_search_widget(self) -> QWidget:
        """Erstellt das Such-Widget"""
        widget = QWidget(self)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Suchfeld
        from PyQt6.QtWidgets import QLineEdit
        search_input = QLineEdit(widget)
        search_input.setPlaceholderText("Suche...")
        search_input.setFixedWidth(200)
        search_input.returnPressed.connect(lambda: self.search_requested.emit(search_input.text()))
        
        layout.addWidget(search_input)
        
        # Such-Button
        search_button = QToolButton(widget)
        search_button.setIcon(QIcon.fromTheme("search"))
        search_button.setToolTip("Suche")
        search_button.clicked.connect(lambda: self.search_requested.emit(search_input.text()))
        
        layout.addWidget(search_button)
        
        return widget
    
    def _on_auth_state_changed(self, authenticated: bool):
        """Wird aufgerufen, wenn sich der Authentifizierungsstatus ändert"""
        # Benutzer-Aktion aktualisieren
        if authenticated:
            self._user_action.setText(auth_manager.current_user.display_name if auth_manager.current_user else "Benutzer")
            self._user_action.setToolTip(f"Angemeldet als: {auth_manager.current_user.username if auth_manager.current_user else 'Unbekannt'}")
        else:
            self._user_action.setText("Benutzer")
            self._user_action.setToolTip("Nicht angemeldet")
    
    def _show_user_menu(self):
        """Zeigt das Benutzer-Menü an"""
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        if auth_manager.is_authenticated:
            # Benutzerinformationen
            user_info_action = QAction(f"Angemeldet als: {auth_manager.current_user.display_name}", self)
            user_info_action.setEnabled(False)
            menu.addAction(user_info_action)
            
            menu.addSeparator()
            
            # Abmelden
            logout_action = QAction("Abmelden", self)
            logout_action.setIcon(QIcon.fromTheme("system-log-out"))
            logout_action.triggered.connect(self._logout)
            menu.addAction(logout_action)
        else:
            # Anmelden
            login_action = QAction("Anmelden", self)
            login_action.setIcon(QIcon.fromTheme("system-log-in"))
            login_action.triggered.connect(self._login)
            menu.addAction(login_action)
        
        menu.exec(self._user_action.icon().actualSize(QSize(16, 16)).toPoint())
    
    def _login(self):
        """Zeigt den Login-Dialog an"""
        from frontend.src.views.login_dialog import LoginDialog
        dialog = LoginDialog(self.parent())
        dialog.exec()
    
    def _logout(self):
        """Meldet den Benutzer ab"""
        from PyQt6.QtWidgets import QMessageBox
        
        result = QMessageBox.question(
            self.parent(),
            "Abmelden",
            "Möchten Sie sich wirklich abmelden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            import asyncio
            async def do_logout():
                await auth_manager.logout()
            
            asyncio.run(do_logout())
