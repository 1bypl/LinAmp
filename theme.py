"""Kolory i arkusz stylów (QSS) aplikacji LinAmp.

Wszystkie kolory trzymamy w jednym miejscu, żeby łatwo zmienić motyw.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

# --- Paleta kolorów ---------------------------------------------------------
BG = "#0f1115"           # tło całego okna
SURFACE = "#151920"      # panele
SURFACE_2 = "#1b2029"    # pola tekstowe, przyciski
SURFACE_3 = "#232a35"    # elementy aktywne / tory suwaków
BORDER = "#262d38"       # delikatne obramowania
TEXT = "#e9edf2"         # podstawowy tekst
MUTED = "#9aa3af"        # tekst drugorzędny
DIM = "#69717d"          # tekst pomocniczy
ACCENT = "#1ed760"       # zielony akcent (przycisk odtwarzania, postęp)
ACCENT_HOVER = "#3ee878"
ACCENT_PRESSED = "#17b34e"
ACCENT_DARK = "#07130a"  # ikona na zielonym tle
DANGER = "#ff5d5d"


QSS = f"""
QWidget {{
    color: {TEXT};
    font-size: 13px;
}}
QMainWindow, QWidget#Root {{
    background-color: {BG};
}}

/* --- Pasek menu --- */
QMenuBar {{
    background-color: {BG};
    color: {MUTED};
    padding: 2px 6px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 6px 10px;
    border-radius: 6px;
}}
QMenuBar::item:selected {{
    background-color: {SURFACE_2};
    color: {TEXT};
}}

/* --- Menu kontekstowe --- */
QMenu {{
    background-color: #171b22;
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px;
}}
QMenu::item {{
    padding: 7px 28px 7px 14px;
    border-radius: 5px;
}}
QMenu::item:selected {{
    background-color: {ACCENT};
    color: {ACCENT_DARK};
}}
QMenu::item:disabled {{
    color: {DIM};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 5px 10px;
}}

/* --- Pola tekstowe --- */
QLineEdit {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {ACCENT};
    selection-color: {ACCENT_DARK};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}
QLineEdit::placeholder {{
    color: {DIM};
}}

/* --- Tabela playlisty --- */
QTableView {{
    background-color: #12151b;
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: #26303e;
    selection-color: {TEXT};
    outline: 0;
}}
QTableView::item {{
    padding: 4px 8px;
    border: none;
}}
QTableView::item:hover {{
    background-color: #1a1f27;
}}
QTableView::item:selected {{
    background-color: #26303e;
}}
QHeaderView::section {{
    background-color: #12151b;
    color: {MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 9px 8px;
    font-weight: 600;
    font-size: 12px;
}}
QHeaderView::section:hover {{
    color: {TEXT};
}}
QTableCornerButton::section {{
    background-color: #12151b;
    border: none;
}}

/* --- Paski przewijania --- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px 2px 2px 0;
}}
QScrollBar::handle:vertical {{
    background: #2f3540;
    border-radius: 5px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: #3d4552;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0 2px 2px 2px;
}}
QScrollBar::handle:horizontal {{
    background: #2f3540;
    border-radius: 5px;
    min-width: 32px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* --- Pasek statusu --- */
QStatusBar {{
    background-color: {BG};
    color: {MUTED};
}}
QStatusBar::item {{
    border: none;
}}

/* --- Etykiety informacyjne --- */
QLabel#NowTitle {{
    font-size: 21px;
    font-weight: 700;
    color: #f3f6f9;
}}
QLabel#NowArtist {{
    font-size: 14px;
    color: #a7b0bb;
}}
QLabel#NowAlbum {{
    font-size: 12px;
    color: {DIM};
}}
QLabel#SectionTitle {{
    font-size: 14px;
    font-weight: 700;
}}
QLabel#Badge {{
    background-color: {SURFACE_2};
    color: {MUTED};
    border-radius: 9px;
    padding: 2px 9px;
    font-size: 11px;
}}
QLabel#VolLabel {{
    color: {MUTED};
    font-size: 11px;
}}

/* --- Lista kategorii radia --- */
QListWidget#RadioCategories {{
    background-color: #12151b;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
    outline: 0;
}}
QListWidget#RadioCategories::item {{
    padding: 8px 10px;
    border-radius: 6px;
    color: {MUTED};
}}
QListWidget#RadioCategories::item:hover {{
    background-color: #1a1f27;
    color: {TEXT};
}}
QListWidget#RadioCategories::item:selected {{
    background-color: {ACCENT};
    color: {ACCENT_DARK};
    font-weight: 600;
}}

/* --- Przyciski akcentowane i radio --- */
QPushButton#AccentButton {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
    color: {ACCENT_DARK};
    font-weight: 700;
    padding: 8px 18px;
    border-radius: 8px;
}}
QPushButton#AccentButton:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}
QPushButton#AccentButton:pressed {{
    background-color: {ACCENT_PRESSED};
}}
QPushButton#AccentButton:disabled {{
    background-color: {SURFACE_2};
    border-color: {BORDER};
    color: {DIM};
}}
QPushButton#RadioButton {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 7px 14px;
    color: {TEXT};
    font-weight: 600;
}}
QPushButton#RadioButton:hover {{
    background-color: {SURFACE_3};
    border-color: {ACCENT};
}}
QPushButton#RadioButton:pressed {{
    background-color: #2b333f;
}}

/* --- Okna dialogowe --- */
QDialog {{
    background-color: {SURFACE};
}}
QPushButton {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 16px;
    color: {TEXT};
}}
QPushButton:hover {{
    background-color: {SURFACE_3};
}}
QPushButton:pressed {{
    background-color: #2b333f;
}}
QPushButton:default {{
    background-color: {ACCENT};
    border-color: {ACCENT};
    color: {ACCENT_DARK};
    font-weight: 600;
}}
QPushButton:default:hover {{
    background-color: {ACCENT_HOVER};
}}
QTextBrowser {{
    background-color: #12151b;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px;
}}
QToolTip {{
    background-color: #20252e;
    color: {TEXT};
    border: 1px solid {BORDER};
    padding: 5px 8px;
}}
QMessageBox {{
    background-color: {SURFACE};
}}
QSplitter::handle {{
    background: transparent;
}}
"""


def apply_theme(app: QApplication) -> None:
    """Ustawia ciemny motyw, czcionkę i spójny styl na wszystkich platformach."""
    app.setStyle("Fusion")

    font = QFont()
    font.setFamilies(["Inter", "Noto Sans", "Segoe UI", "DejaVu Sans"])
    font.setPointSizeF(10.0)
    app.setFont(font)

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG))
    palette.setColor(QPalette.ColorRole.Base, QColor(SURFACE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE_2))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(SURFACE_2))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(ACCENT_DARK))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(SURFACE_2))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(DIM))
    app.setPalette(palette)

    app.setStyleSheet(QSS)
