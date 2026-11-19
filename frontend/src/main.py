"""
Sailight Frontend - Hauptanwendung
PyQt6-Anwendung für Straßenbeleuchtungsverwaltung
"""

import sys
import logging
import traceback
from typing import Optional

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSlot

from frontend.src.config import config
from frontend.src.utils.theme import apply_theme
from frontend.src.utils.logging import setup_logging, get_logger
from frontend.src.views.main_window import MainWindow

logger = get_logger("sailight.main")


class SailightApplication(QApplication):
    """Hauptanwendungsklasse"""
    
    def __init__(self, argv: list):
        """Initialisiert die Anwendung"""
        super().__init__(argv)
        
        # Anwendungskonfiguration
        self.setApplicationName(config.APP_NAME)
        self.setApplicationVersion(config.APP_VERSION)
        self.setOrganizationName("Administration des Ponts et Chaussées")
        self.setOrganizationDomain("sailight.lu")
        
        # Fenster-Icon (falls verfügbar)
        try:
            self.setWindowIcon(QIcon("resources/icons/sailight.png"))
        except Exception:
            pass
        
        # Thema anwenden
        apply_theme(self)
        
        # Font setzen
        font = QFont()
        font.setFamily("Segoe UI" if sys.platform == "win32" else "DejaVu Sans")
        font.setPointSize(10)
        self.setFont(font)
        
        # Splash Screen (optional)
        self._splash_screen: Optional[QSplashScreen] = None
        
        # Hauptfenster
        self._main_window: Optional[MainWindow] = None
        
        # Initialisierung
        self._initialize()
    
    def _initialize(self):
        """Initialisiert die Anwendung"""
        try:
            # Splash Screen anzeigen
            self.show_splash_screen()
            
            # Hauptfenster erstellen
            self._main_window = MainWindow()
            
            # Splash Screen schließen
            self.hide_splash_screen()
            
            # Hauptfenster anzeigen
            self._main_window.show()
            
            logger.info("Anwendung erfolgreich gestartet")
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Anwendung: {e}")
            traceback.print_exc()
            self.show_error_message(
                "Fehler beim Starten",
                f"Die Anwendung konnte nicht gestartet werden:\n\n{str(e)}"
            )
            self.quit()
    
    def show_splash_screen(self):
        """Zeigt den Splash Screen an"""
        try:
            # Splash Screen erstellen
            splash_pixmap = QPixmap("resources/icons/splash.png")
            if splash_pixmap.isNull():
                # Standard Splash Screen
                splash_pixmap = QPixmap(400, 300)
                splash_pixmap.fill(Qt.GlobalColor.black)
            
            self._splash_screen = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
            self._splash_screen.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
            
            # Status anzeigen
            self._splash_screen.show()
            self._splash_screen.showMessage(
                "Sailight wird gestartet...",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                Qt.GlobalColor.white
            )
            
            # Application verarbeiten
            self.processEvents()
            
        except Exception as e:
            logger.warning(f"Splash Screen konnte nicht angezeigt werden: {e}")
    
    def hide_splash_screen(self):
        """Schließt den Splash Screen"""
        if self._splash_screen:
            self._splash_screen.finish(self._main_window)
            self._splash_screen = None
    
    def show_error_message(self, title: str, message: str):
        """Zeigt eine Fehlermeldung an"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


def main():
    """Hauptfunktion"""
    try:
        # Logging initialisieren
        setup_logging(config.LOG_LEVEL, config.LOG_FILE)
        
        logger.info("Sailight Frontend wird gestartet...")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"PyQt6 Version: {__import__('PyQt6').__version__}")
        
        # Anwendung erstellen
        app = SailightApplication(sys.argv)
        
        # Anwendung ausführen
        sys.exit(app.exec())
        
    except Exception as e:
        # Fehlerbehandlung
        print(f"Kritischer Fehler: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
