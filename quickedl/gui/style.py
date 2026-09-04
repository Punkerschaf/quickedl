"""Application stylesheet -- a compact, restrained dark theme suited to a control room."""

ACCENT = "#4A9EFF"
BACKGROUND = "#1E2126"
SURFACE = "#282C34"
SURFACE_RAISED = "#31363F"
BORDER = "#3C424D"
TEXT = "#E4E7EB"
TEXT_MUTED = "#9BA3AF"
DANGER = "#E05252"
OK_GREEN = "#5CBF7A"

STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-size: 11px;
}}

QMainWindow, QDialog {{
    background-color: {BACKGROUND};
}}

QLabel[role="title"] {{
    font-size: 14px;
    font-weight: 600;
}}

QLabel[role="muted"] {{
    color: {TEXT_MUTED};
}}

QLabel[role="playlist"] {{
    font-size: 13px;
    font-weight: 600;
}}

QLabel[role="hotkeys-on"] {{
    color: {OK_GREEN};
    font-weight: 600;
}}

QLabel[role="hotkeys-off"] {{
    color: {TEXT_MUTED};
}}

QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 5px;
    margin-top: 9px;
    padding: 7px 6px 6px 6px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 3px;
    color: {TEXT_MUTED};
}}

QPushButton {{
    background-color: {SURFACE_RAISED};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 9px;
}}

QPushButton:hover {{
    background-color: #3A404B;
    border-color: {ACCENT};
}}

QPushButton:pressed {{
    background-color: {ACCENT};
    color: #10141A;
}}

QPushButton:disabled {{
    color: {TEXT_MUTED};
    background-color: {SURFACE};
}}

QPushButton[role="marker"] {{
    font-size: 13px;
    font-weight: 700;
    padding: 3px;
}}

QPushButton[role="primary"] {{
    background-color: {ACCENT};
    border-color: {ACCENT};
    color: #10141A;
    font-weight: 600;
}}

QPushButton[role="danger"]:hover {{
    border-color: {DANGER};
    color: {DANGER};
}}

QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QComboBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 3px 6px;
    selection-background-color: {ACCENT};
    selection-color: #10141A;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QDateEdit:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}

QTableWidget, QListWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    gridline-color: {BORDER};
    selection-background-color: {ACCENT};
    selection-color: #10141A;
}}

QHeaderView::section {{
    background-color: {SURFACE_RAISED};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 3px 6px;
    font-weight: 600;
}}

QMenuBar, QMenu {{
    background-color: {SURFACE};
}}

QMenuBar::item {{
    padding: 3px 8px;
}}

QMenuBar::item:selected, QMenu::item:selected {{
    background-color: {ACCENT};
    color: #10141A;
}}

QStatusBar {{
    background-color: {SURFACE};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
}}

QStatusBar::item {{
    border: none;
}}

QToolButton {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 2px;
}}

QToolButton:hover {{
    border-color: {ACCENT};
}}

QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {SURFACE};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
"""
