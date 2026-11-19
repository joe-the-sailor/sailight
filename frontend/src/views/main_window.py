"""
Hauptfenster der Sailight-Anwendung
Multi-Window-Workspace mit Docking-System
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QDockWidget, QTabWidget, QSplitter, QStackedWidget,
    QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from typing import Optional, Dict, Any
import logging

from frontend.src.config import config
from frontend.src.utils.auth import auth_manager, User
from frontend.src.views.toolbar import ToolBar
from frontend.src.views.status_bar import StatusBar
from frontend.src.views.dashboard_view import DashboardView
from frontend.src.views.cabinet_view import CabinetView
from frontend.src.views.light_point_view import LightPointView
from frontend.src.views.pole_view import PoleView
from frontend.src.views.circuit_group_view import CircuitGroupView
from frontend.src.views.map_view import MapView
from frontend.src.views.filter_panel import FilterPanel
from frontend.src.views.detail_view import DetailView
from frontend.src.views.login_dialog import LoginDialog

logger = logging.getLogger("sailight.main_window")


class MainWindow(QMainWindow):
    """Hauptfenster mit Multi-Window-Workspace"""
    
    # Signale
    view_changed = pyqtSignal(str)  # Aktuelle Ansicht geändert
    
    def __init__(self):
        """Initialisiert das Hauptfenster"""
        super().__init__()
        
        # Fenster-Eigenschaften
        self.setWindowTitle(config.APP_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Menüleiste erstellen
        self._create_menu_bar()
        
        # Toolbar erstellen
        self._toolbar = ToolBar(self)
        self.addToolBar(self._toolbar)
        
        # Statusleiste erstellen
        self._status_bar = StatusBar(self)
        self.setStatusBar(self._status_bar)
        
        # Zentrales Widget und Layout
        self._central_widget = QWidget(self)
        self._central_layout = QVBoxLayout(self._central_widget)
        self._central_layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout.setSpacing(0)
        
        # Haupt-Splitter für Multi-Window-Layout
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal, self._central_widget)
        self._main_splitter.setContentsMargins(0, 0, 0, 0)
        self._main_splitter.setHandleWidth(4)
        self._central_layout.addWidget(self._main_splitter)
        
        # Linkes Dock: Filter und Navigation
        self._filter_dock = self._create_filter_dock()
        
        # Haupt-Tab-Widget für die zentralen Ansichten
        self._main_tab_widget = QTabWidget(self._central_widget)
        self._main_tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self._main_tab_widget.setMovable(True)
        self._main_tab_widget.setTabsClosable(True)
        self._main_tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        
        # Rechter Bereich: Tab-Widget
        self._main_splitter.addWidget(self._filter_dock)
        self._main_splitter.addWidget(self._main_tab_widget)
        
        # Ansichten initialisieren
        self._views: Dict[str, QWidget] = {}
        self._initialize_views()
        
        # Standardansicht setzen
        self._show_view("dashboard")
        
        # Auth-Manager Signale verbinden
        self._connect_auth_signals()
        
        # Fenster-Eigenschaften
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks
        )
        
        # Dock-Widgets standardmäßig sichtbar
        self._filter_dock.setVisible(True)
        
        # Splitter-Verhältnis
        self._main_splitter.setStretchFactor(0, 1)  # Filter-Dock
        self._main_splitter.setStretchFactor(1, 3)  # Hauptbereich
        
        # Timer für Status-Updates
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(1000)  # Alle 1 Sekunde
        
        logger.info("Hauptfenster initialisiert")
    
    def _create_menu_bar(self):
        """Erstellt die Menüleiste"""
        menu_bar = self.menuBar()
        
        # Datei-Menü
        file_menu = menu_bar.addMenu("Datei")
        
        # Bearbeiten-Menü
        edit_menu = menu_bar.addMenu("Bearbeiten")
        
        # Ansicht-Menü
        view_menu = menu_bar.addMenu("Ansicht")
        
        # Fenster-Menü
        window_menu = menu_bar.addMenu("Fenster")
        
        # Hilfe-Menü
        help_menu = menu_bar.addMenu("Hilfe")
        
        # Aktionen für Datei-Menü
        login_action = QAction("Anmelden", self)
        login_action.setShortcut(QKeySequence("Ctrl+L"))
        login_action.triggered.connect(self._show_login_dialog)
        file_menu.addAction(login_action)
        
        logout_action = QAction("Abmelden", self)
        logout_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        logout_action.triggered.connect(self._logout)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Aktionen für Ansicht-Menü
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self._show_view("dashboard"))
        view_menu.addAction(dashboard_action)
        
        view_menu.addSeparator()
        
        map_action = QAction("Karte", self)
        map_action.triggered.connect(lambda: self._show_view("map"))
        view_menu.addAction(map_action)
        
        view_menu.addSeparator()
        
        cabinet_action = QAction("Schaltschränke", self)
        cabinet_action.triggered.connect(lambda: self._show_view("cabinets"))
        view_menu.addAction(cabinet_action)
        
        light_point_action = QAction("Leuchtstellen", self)
        light_point_action.triggered.connect(lambda: self._show_view("light_points"))
        view_menu.addAction(light_point_action)
        
        pole_action = QAction("Masten", self)
        pole_action.triggered.connect(lambda: self._show_view("poles"))
        view_menu.addAction(pole_action)
        
        circuit_group_action = QAction("Leitungsgruppen", self)
        circuit_group_action.triggered.connect(lambda: self._show_view("circuit_groups"))
        view_menu.addAction(circuit_group_action)
        
        # Aktionen für Hilfe-Menü
        about_action = QAction("Über Sailight", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_filter_dock(self) -> QDockWidget:
        """Erstellt das Filter-Dock-Widget"""
        dock = QDockWidget("Filter & Suche", self)
        dock.setObjectName("FilterDock")
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        
        # Filter-Panel erstellen
        filter_panel = FilterPanel(dock)
        dock.setWidget(filter_panel)
        
        return dock
    
    def _initialize_views(self):
        """Initialisiert alle Ansichten"""
        # Dashboard
        self._views["dashboard"] = DashboardView(self._main_tab_widget)
        
        # Karte
        self._views["map"] = MapView(self._main_tab_widget)
        
        # Schaltschränke
        self._views["cabinets"] = CabinetView(self._main_tab_widget)
        
        # Leuchtstellen
        self._views["light_points"] = LightPointView(self._main_tab_widget)
        
        # Masten
        self._views["poles"] = PoleView(self._main_tab_widget)
        
        # Leitungsgruppen
        self._views["circuit_groups"] = CircuitGroupView(self._main_tab_widget)
        
        # Detailansicht
        self._views["detail"] = DetailView(self._main_tab_widget)
    
    def _show_view(self, view_name: str, params: Optional[Dict[str, Any]] = None):
        """Zeigt eine bestimmte Ansicht an"""
        if view_name not in self._views:
            logger.warning(f"Ansicht '{view_name}' nicht gefunden")
            return
        
        view = self._views[view_name]
        
        # Prüfen, ob die Ansicht bereits als Tab geöffnet ist
        for i in range(self._main_tab_widget.count()):
            if self._main_tab_widget.widget(i) == view:
                self._main_tab_widget.setCurrentIndex(i)
                return
        
        # Neue Ansicht als Tab hinzufügen
        index = self._main_tab_widget.addTab(view, view.windowTitle())
        self._main_tab_widget.setCurrentIndex(index)
        
        # Signale auslösen
        self.view_changed.emit(view_name)
        
        # Status aktualisieren
        self._status_bar.set_current_view(view_name)
        
        logger.info(f"Ansicht '{view_name}' angezeigt")
    
    def _on_tab_close_requested(self, index: int):
        """Wird aufgerufen, wenn ein Tab geschlossen werden soll"""
        widget = self._main_tab_widget.widget(index)
        
        # Prüfen, ob das Widget eine Ansicht ist, die nicht geschlossen werden darf
        if widget.objectName() in ["dashboard", "map"]:
            # Dashboard und Karte nicht schließen
            return
        
        # Tab schließen
        self._main_tab_widget.removeTab(index)
        widget.deleteLater()
        
        logger.info(f"Tab {index} geschlossen")
    
    def _connect_auth_signals(self):
        """Verbindet die Auth-Manager-Signale"""
        auth_manager.auth_state_changed.connect(self._on_auth_state_changed)
        auth_manager.user_changed.connect(self._on_user_changed)
        auth_manager.login_success.connect(self._on_login_success)
        auth_manager.login_failed.connect(self._on_login_failed)
        auth_manager.logout_success.connect(self._on_logout_success)
    
    def _on_auth_state_changed(self, authenticated: bool):
        """Wird aufgerufen, wenn sich der Authentifizierungsstatus ändert"""
        if authenticated:
            self._status_bar.set_auth_status("Angemeldet")
        else:
            self._status_bar.set_auth_status("Nicht angemeldet")
        
        # Menüleiste aktualisieren
        self._update_menu_bar()
    
    def _on_user_changed(self, user: User):
        """Wird aufgerufen, wenn sich der Benutzer ändert"""
        if user:
            self._status_bar.set_user_info(user.display_name, user.roles)
        else:
            self._status_bar.set_user_info("", [])
    
    def _on_login_success(self, user: User):
        """Wird aufgerufen, wenn die Anmeldung erfolgreich war"""
        logger.info(f"Benutzer '{user.username}' erfolgreich angemeldet")
        self._status_bar.show_message(f"Willkommen, {user.display_name}!", 3000)
    
    def _on_login_failed(self, error: str):
        """Wird aufgerufen, wenn die Anmeldung fehlgeschlagen ist"""
        logger.error(f"Anmeldung fehlgeschlagen: {error}")
        self._status_bar.show_message(f"Anmeldung fehlgeschlagen: {error}", 3000)
    
    def _on_logout_success(self):
        """Wird aufgerufen, wenn die Abmeldung erfolgreich war"""
        logger.info("Benutzer erfolgreich abgemeldet")
        self._status_bar.show_message("Erfolgreich abgemeldet", 3000)
    
    def _update_menu_bar(self):
        """Aktualisiert die Menüleiste basierend auf dem Auth-Status"""
        # Menüleiste finden
        menu_bar = self.menuBar()
        
        # Aktionen finden
        login_action = None
        logout_action = None
        
        for action in menu_bar.actions():
            if action.text() == "Anmelden":
                login_action = action
            elif action.text() == "Abmelden":
                logout_action = action
        
        # Sichtbarkeit anpassen
        if auth_manager.is_authenticated:
            if login_action:
                login_action.setVisible(False)
            if logout_action:
                logout_action.setVisible(True)
        else:
            if login_action:
                login_action.setVisible(True)
            if logout_action:
                logout_action.setVisible(False)
    
    def _show_login_dialog(self):
        """Zeigt den Login-Dialog an"""
        dialog = LoginDialog(self)
        dialog.exec()
    
    def _logout(self):
        """Meldet den Benutzer ab"""
        # Bestätigung anzeigen
        result = QMessageBox.question(
            self,
            "Abmelden",
            "Möchten Sie sich wirklich abmelden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Asynchronen Logout durchführen
            import asyncio
            async def do_logout():
                await auth_manager.logout()
            
            # In einem separaten Thread ausführen
            thread = QThread(self)
            worker = AsyncWorker(do_logout, thread)
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            thread.start()
    
    def _show_about_dialog(self):
        """Zeigt den Über-Dialog an"""
        about_text = f"""
        <h2>{config.APP_NAME} v{config.APP_VERSION}</h2>
        <p>Straßenbeleuchtungsverwaltung für Administration des Ponts et Chaussées, Luxemburg</p>
        <p>&copy; 2024 Joe the Sailor</p>
        <p>Basierend auf Python, PyQt6 und FastAPI</p>
        """
        
        QMessageBox.about(self, "Über Sailight", about_text)
    
    def _update_status(self):
        """Aktualisiert den Status"""
        # Zeit aktualisieren
        self._status_bar.update_time()
        
        # Auth-Status prüfen
        if auth_manager.is_authenticated:
            self._status_bar.set_auth_status("Angemeldet")
        else:
            self._status_bar.set_auth_status("Nicht angemeldet")
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # Bestätigung anzeigen
        result = QMessageBox.question(
            self,
            "Beenden",
            "Möchten Sie die Anwendung wirklich beenden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Auth-Manager bereinigen
            import asyncio
            async def cleanup():
                await auth_manager.logout()
                await self._views["map"].cleanup() if "map" in self._views else None
            
            # Synchron ausführen (einfachere Lösung für Close-Event)
            try:
                import asyncio
                asyncio.run(cleanup())
            except Exception:
                pass
            
            event.accept()
        else:
            event.ignore()


class AsyncWorker(QObject):
    """Hilfsklasse für asynchrone Operationen in QThreads"""
    
    def __init__(self, coro, parent=None):
        super().__init__(parent)
        self.coro = coro
    
    def run(self):
        """Führt die asynchrone Funktion aus"""
        import asyncio
        asyncio.run(self.coro())
