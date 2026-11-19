"""
Themen-Manager für die PyQt6-Anwendung
Dark Theme mit orange Akzenten
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon
from PyQt6.QtWidgets import QApplication, QStyleFactory
from typing import Optional

from frontend.src.config import config


def get_theme_stylesheet() -> str:
    """
    Gibt das Stylesheet für das Dark Theme mit orange Akzenten zurück
    """
    return f"""
    /* Hauptfenster */
    QMainWindow {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: none;
    }}
    
    /* Zentrales Widget */
    QWidget {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        selection-background-color: {config.PRIMARY_COLOR};
        selection-color: {config.BACKGROUND_COLOR};
    }}
    
    /* Überschriften */
    QLabel[heading="true"] {{
        color: {config.PRIMARY_COLOR};
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    
    QLabel[subheading="true"] {{
        color: {config.TEXT_SECONDARY};
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 6px 12px;
        min-width: 80px;
        font-size: 12px;
    }}
    
    QPushButton:hover {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
        border-color: {config.PRIMARY_COLOR};
    }}
    
    QPushButton:pressed {{
        background-color: {config.SECONDARY_COLOR};
        border-color: {config.SECONDARY_COLOR};
    }}
    
    QPushButton:disabled {{
        background-color: {config.BORDER_COLOR};
        color: {config.TEXT_SECONDARY};
        border-color: {config.BORDER_COLOR};
    }}
    
    QPushButton[primary="true"] {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
        border: none;
        font-weight: bold;
    }}
    
    QPushButton[primary="true"]:hover {{
        background-color: {config.SECONDARY_COLOR};
    }}
    
    QPushButton[primary="true"]:pressed {{
        background-color: {config.ACCENT_COLOR};
    }}
    
    QPushButton[danger="true"] {{
        background-color: {config.ERROR_COLOR};
        color: white;
        border: none;
    }}
    
    QPushButton[danger="true"]:hover {{
        background-color: #ff5c5c;
    }}
    
    QPushButton[success="true"] {{
        background-color: {config.SUCCESS_COLOR};
        color: white;
        border: none;
    }}
    
    QPushButton[success="true"]:hover {{
        background-color: #4caf70;
    }}
    
    /* ToolButtons */
    QToolButton {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    
    QToolButton:hover {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    QToolButton:pressed {{
        background-color: {config.SECONDARY_COLOR};
    }}
    
    /* TabWidget */
    QTabWidget {{
        background-color: {config.SURFACE_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
    }}
    
    QTabWidget::pane {{
        background-color: {config.SURFACE_COLOR};
        border: none;
        border-radius: 0;
    }}
    
    QTabBar::tab {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_SECONDARY};
        border: 1px solid {config.BORDER_COLOR};
        border-bottom: none;
        padding: 8px 16px;
        min-width: 100px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {config.SURFACE_COLOR};
        color: {config.PRIMARY_COLOR};
        border-color: {config.PRIMARY_COLOR};
        border-bottom-color: {config.SURFACE_COLOR};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    /* TableView */
    QTableView {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        gridline-color: {config.BORDER_COLOR};
        selection-background-color: {config.PRIMARY_COLOR};
        selection-color: {config.BACKGROUND_COLOR};
    }}
    
    QHeaderView {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: none;
        border-bottom: 1px solid {config.BORDER_COLOR};
        padding: 4px;
    }}
    
    QHeaderView::section {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: none;
        border-right: 1px solid {config.BORDER_COLOR};
        padding: 6px;
        font-weight: bold;
        text-align: left;
    }}
    
    QHeaderView::section:last {{
        border-right: none;
    }}
    
    QHeaderView::section:hover {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    QTableView::item:alternate {{
        background-color: {config.TABLE_ALTERNATE_COLOR};
    }}
    
    QTableView::item:selected {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    QTableView::item:hover {{
        background-color: {config.ACCENT_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    /* LineEdit */
    QLineEdit {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
        selection-background-color: {config.PRIMARY_COLOR};
        selection-color: {config.BACKGROUND_COLOR};
    }}
    
    QLineEdit:focus {{
        border-color: {config.PRIMARY_COLOR};
    }}
    
    QLineEdit:read-only {{
        background-color: {config.BORDER_COLOR};
        color: {config.TEXT_SECONDARY};
    }}
    
    /* TextEdit */
    QTextEdit {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
        selection-background-color: {config.PRIMARY_COLOR};
        selection-color: {config.BACKGROUND_COLOR};
    }}
    
    QTextEdit:focus {{
        border-color: {config.PRIMARY_COLOR};
    }}
    
    /* ComboBox */
    QComboBox {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
        min-width: 100px;
    }}
    
    QComboBox:focus {{
        border-color: {config.PRIMARY_COLOR};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        selection-background-color: {config.PRIMARY_COLOR};
        selection-color: {config.BACKGROUND_COLOR};
    }}
    
    QComboBox::drop-down {{
        border: none;
    }}
    
    /* SpinBox */
    QSpinBox, QDoubleSpinBox {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {config.PRIMARY_COLOR};
    }}
    
    /* DateEdit */
    QDateEdit {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QDateEdit:focus {{
        border-color: {config.PRIMARY_COLOR};
    }}
    
    /* CheckBox */
    QCheckBox {{
        spacing: 8px;
        color: {config.TEXT_COLOR};
    }}
    
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {config.PRIMARY_COLOR};
        border: 1px solid {config.PRIMARY_COLOR};
    }}
    
    QCheckBox::indicator:unchecked {{
        background-color: {config.BACKGROUND_COLOR};
        border: 1px solid {config.BORDER_COLOR};
    }}
    
    /* RadioButton */
    QRadioButton {{
        spacing: 8px;
        color: {config.TEXT_COLOR};
    }}
    
    QRadioButton::indicator {{
        width: 16px;
        height: 16px;
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {config.PRIMARY_COLOR};
        border: 1px solid {config.PRIMARY_COLOR};
    }}
    
    QRadioButton::indicator:unchecked {{
        background-color: {config.BACKGROUND_COLOR};
        border: 1px solid {config.BORDER_COLOR};
    }}
    
    /* GroupBox */
    QGroupBox {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 15px;
        padding-bottom: 5px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: {config.PRIMARY_COLOR};
        font-weight: bold;
    }}
    
    /* ScrollArea */
    QScrollArea {{
        background-color: {config.SURFACE_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
    }}
    
    QScrollBar:vertical {{
        background-color: {config.BACKGROUND_COLOR};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {config.PRIMARY_COLOR};
        min-height: 20px;
        border-radius: 6px;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
        border: none;
    }}
    
    QScrollBar:horizontal {{
        background-color: {config.BACKGROUND_COLOR};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {config.PRIMARY_COLOR};
        min-width: 20px;
        border-radius: 6px;
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none;
        border: none;
    }}
    
    /* StatusBar */
    QStatusBar {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_SECONDARY};
        border-top: 1px solid {config.BORDER_COLOR};
        padding: 4px;
    }}
    
    /* MenuBar */
    QMenuBar {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border-bottom: 1px solid {config.BORDER_COLOR};
        padding: 2px;
    }}
    
    QMenuBar::item {{
        padding: 6px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    /* Menu */
    QMenu {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        background-color: transparent;
    }}
    
    QMenu::item:selected {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    QMenu::item:disabled {{
        color: {config.TEXT_SECONDARY};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {config.BORDER_COLOR};
        margin: 4px 0;
    }}
    
    /* ToolBar */
    QToolBar {{
        background-color: {config.BACKGROUND_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        padding: 4px;
    }}
    
    QToolBar::separator {{
        width: 1px;
        background-color: {config.BORDER_COLOR};
        margin: 4px 0;
    }}
    
    /* DockWidget */
    QDockWidget {{
        background-color: {config.SURFACE_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
    }}
    
    QDockWidget::title {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: none;
        border-bottom: 1px solid {config.BORDER_COLOR};
        padding: 6px;
        text-align: left;
    }}
    
    QDockWidget::close-button, QDockWidget::float-button {{
        background-color: transparent;
        border: none;
        icon-size: 12px;
    }}
    
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
        background-color: {config.ERROR_COLOR};
    }}
    
    /* ProgressBar */
    QProgressBar {{
        background-color: {config.BACKGROUND_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {config.PRIMARY_COLOR};
        border-radius: 4px;
    }}
    
    /* MessageBox */
    QMessageBox {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
    }}
    
    QMessageBox QLabel {{
        color: {config.TEXT_COLOR};
    }}
    
    QMessageBox QPushButton {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        padding: 6px 12px;
        min-width: 80px;
    }}
    
    QMessageBox QPushButton:hover {{
        background-color: {config.PRIMARY_COLOR};
        color: {config.BACKGROUND_COLOR};
    }}
    
    /* InputDialog */
    QInputDialog {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
    }}
    
    QInputDialog QLineEdit {{
        background-color: {config.BACKGROUND_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        padding: 6px;
    }}
    
    QInputDialog QLabel {{
        color: {config.TEXT_COLOR};
    }}
    
    /* TreeView */
    QTreeView {{
        background-color: {config.SURFACE_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.BORDER_COLOR};
        border-radius: 4px;
        selection-background-color: {config.PRIMARY_COLOR};
        selection-color: {config.BACKGROUND_COLOR};
    }}
    
    QTreeView::item:alternate {{
        background-color: {config.TABLE_ALTERNATE_COLOR};
    }}
    
    /* Splitter */
    QSplitter {{
        background-color: {config.BACKGROUND_COLOR};
    }}
    
    QSplitter::handle {{
        background-color: {config.BORDER_COLOR};
        width: 4px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {config.PRIMARY_COLOR};
    }}
    
    /* Status Tip */
    QWidget[statusTip="true"] {{
        color: {config.TEXT_SECONDARY};
    }}
    """


def apply_theme(app: Optional['QApplication'] = None):
    """
    Wendet das Dark Theme auf die Anwendung an
    
    Args:
        app: QApplication-Instanz (optional, wird automatisch erkannt)
    """
    if app is None:
        app = QApplication.instance()
    
    if app is None:
        return
    
    # Standard-Palette auf Dark setzen
    palette = app.palette()
    
    # Farben setzen
    palette.setColor(QPalette.ColorRole.Window, QColor(config.BACKGROUND_COLOR))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(config.TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.Base, QColor(config.BACKGROUND_COLOR))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(config.TABLE_ALTERNATE_COLOR))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(config.BACKGROUND_COLOR))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(config.TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.Text, QColor(config.TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.Button, QColor(config.SURFACE_COLOR))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(config.TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(config.PRIMARY_COLOR))
    palette.setColor(QPalette.ColorRole.Link, QColor(config.PRIMARY_COLOR))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(config.PRIMARY_COLOR))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(config.BACKGROUND_COLOR))
    
    # Deaktivierte Farben
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.Text, QColor(config.TEXT_SECONDARY))
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.ButtonText, QColor(config.TEXT_SECONDARY))
    
    app.setPalette(palette)
    
    # Stylesheet anwenden
    app.setStyleSheet(get_theme_stylesheet())
    
    # Style auf Fusion setzen (bessere Unterstützung für Stylesheets)
    app.setStyle(QStyleFactory.create("Fusion"))
