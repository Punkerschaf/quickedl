"""Reusable widgets: color picking and the marker list."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
)

from ..core.colorset import ColorSet
from ..core.models import Marker, MarkerType

NO_COLOR_LABEL = "Keine Farbe"


def color_swatch(hex_color: str | None, size: int = 16) -> QIcon:
    """Build a small square icon for a color (or an empty outline for None)."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    if hex_color:
        painter.setBrush(QColor(hex_color))
        painter.setPen(QPen(QColor("#00000060"), 1))
    else:
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#9BA3AF"), 1, Qt.DashLine))
    painter.drawRoundedRect(1, 1, size - 2, size - 2, 3, 3)
    painter.end()
    return QIcon(pixmap)


class ColorSelectButton(QToolButton):
    """Pick one color out of the project's color set (or none)."""

    colorChanged = Signal(object)  # str | None

    def __init__(self, colorset: ColorSet | None = None, color_id: str | None = None, parent=None) -> None:
        super().__init__(parent)
        self._colorset = colorset
        self._color_id = color_id
        self.setPopupMode(QToolButton.InstantPopup)
        self.setIconSize(QSize(16, 16))
        self.setMenu(QMenu(self))
        self.setToolTip("Farbe wählen")
        self._rebuild()

    def set_colorset(self, colorset: ColorSet | None) -> None:
        self._colorset = colorset
        if colorset is not None and colorset.get(self._color_id) is None:
            self._color_id = None
        self._rebuild()

    def color_id(self) -> str | None:
        return self._color_id

    def set_color_id(self, color_id: str | None) -> None:
        self._color_id = color_id
        self._update_icon()

    def _rebuild(self) -> None:
        menu = self.menu()
        menu.clear()

        none_action = QAction(color_swatch(None), NO_COLOR_LABEL, self)
        none_action.triggered.connect(lambda: self._choose(None))
        menu.addAction(none_action)

        if self._colorset:
            menu.addSeparator()
            for color in self._colorset.colors:
                action = QAction(color_swatch(color.display_color), color.label, self)
                action.triggered.connect(lambda _checked=False, cid=color.id: self._choose(cid))
                menu.addAction(action)
        self._update_icon()

    def _choose(self, color_id: str | None) -> None:
        self._color_id = color_id
        self._update_icon()
        self.colorChanged.emit(color_id)

    def _update_icon(self) -> None:
        hex_color = self._colorset.display_color_of(self._color_id, "") if self._colorset else ""
        self.setIcon(color_swatch(hex_color or None))
        color = self._colorset.get(self._color_id) if self._colorset else None
        self.setToolTip(f"Farbe: {color.label}" if color else f"Farbe: {NO_COLOR_LABEL}")


class MarkerTable(QTableWidget):
    """Chronological list of the markers logged so far."""

    COLUMNS = ("", "Zeit", "Label", "Typ")

    TYPE_LABELS = {
        MarkerType.LABEL: "Label",
        MarkerType.POPUP: "Popup",
        MarkerType.PLAYLIST: "Playlist",
        MarkerType.SEPARATOR: "Trenner",
    }

    def __init__(self, parent=None) -> None:
        super().__init__(0, len(self.COLUMNS), parent)
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.setColumnWidth(0, 22)

    def refresh(self, markers: list[Marker], colorset: ColorSet | None) -> None:
        self.setRowCount(len(markers))
        for row, marker in enumerate(markers):
            hex_color = colorset.display_color_of(marker.color, "") if colorset else ""

            swatch = QTableWidgetItem()
            if hex_color:
                swatch.setBackground(QColor(hex_color))
            self.setItem(row, 0, swatch)

            self.setItem(row, 1, QTableWidgetItem("" if marker.is_separator else marker.time_string))
            label = "─" * 12 if marker.is_separator else marker.label
            self.setItem(row, 2, QTableWidgetItem(label))
            self.setItem(row, 3, QTableWidgetItem(self.TYPE_LABELS.get(marker.type, "")))
        self.scrollToBottom()
