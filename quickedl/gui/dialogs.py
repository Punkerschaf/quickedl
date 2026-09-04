"""Dialogs: new project, project settings, popup marker, playlist editor."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from ..core.colorset import ColorSet
from ..core.project import Project, suggest_project_path
from .widgets import NO_COLOR_LABEL, color_swatch


def _color_combo(colorset: ColorSet | None, selected: str | None) -> QComboBox:
    combo = QComboBox()
    combo.addItem(color_swatch(None), NO_COLOR_LABEL, None)
    if colorset:
        for color in colorset.colors:
            combo.addItem(color_swatch(color.display_color), color.label, color.id)
    index = combo.findData(selected)
    combo.setCurrentIndex(index if index >= 0 else 0)
    return combo


class NewProjectDialog(QDialog):
    """Collect everything needed to create a new project file."""

    def __init__(self, colorsets: dict[str, ColorSet], default_dir: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Neues Projekt")
        self.setMinimumWidth(460)
        self._colorsets = colorsets

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("z.B. Sommerkonzert 2026")

        self.dir_edit = QLineEdit(str(default_dir))
        browse_button = QPushButton("…")
        browse_button.setFixedWidth(36)
        browse_button.clicked.connect(self._browse)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self.dir_edit)
        dir_row.addWidget(browse_button)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")

        self.colorset_combo = QComboBox()
        for colorset in colorsets.values():
            self.colorset_combo.addItem(colorset.name, colorset.id)

        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("Notizen zum Projekt (optional)")
        self.notes_edit.setFixedHeight(80)

        form = QFormLayout()
        form.addRow("Projektname", self.name_edit)
        form.addRow("Speicherort", dir_row)
        form.addRow("Produktionsdatum", self.date_edit)
        form.addRow("Color-Set", self.colorset_combo)
        form.addRow("Notizen", self.notes_edit)

        hint = QLabel("Das Color-Set legt fest, welche Marker-Farben zur Verfügung stehen, "
                      "und lässt sich später nicht mehr wechseln.")
        hint.setWordWrap(True)
        hint.setProperty("role", "muted")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Projekt anlegen")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addWidget(buttons)

        self.project: Project | None = None

    def _browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Speicherort wählen", self.dir_edit.text())
        if directory:
            self.dir_edit.setText(directory)

    def _accept(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Projektname fehlt", "Bitte einen Projektnamen eingeben.")
            return

        directory = Path(self.dir_edit.text().strip() or Path.home())
        target = suggest_project_path(directory, name)
        if target.exists():
            answer = QMessageBox.question(
                self,
                "Datei existiert",
                f"{target.name} existiert bereits.\nSoll die Datei überschrieben werden?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return

        qdate = self.date_edit.date()
        try:
            self.project = Project.create(
                name=name,
                path=target,
                color_set=self.colorset_combo.currentData(),
                production_date=date(qdate.year(), qdate.month(), qdate.day()),
                notes=self.notes_edit.toPlainText(),
            )
        except Exception as error:  # surfaced to the user rather than swallowed
            QMessageBox.critical(self, "Projekt konnte nicht angelegt werden", str(error))
            return
        self.accept()


class ProjectSettingsDialog(QDialog):
    """Edit project metadata and the default colors for popup/playlist markers."""

    def __init__(self, project: Project, colorset: ColorSet | None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Projekt-Einstellungen")
        self.setMinimumWidth(460)
        self._project = project

        self.name_edit = QLineEdit(project.name)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        if project.production_date:
            self.date_edit.setDate(QDate(project.production_date.year,
                                         project.production_date.month,
                                         project.production_date.day))
        else:
            self.date_edit.setDate(QDate.currentDate())

        self.notes_edit = QPlainTextEdit(project.notes)
        self.notes_edit.setFixedHeight(100)

        colorset_label = QLabel(colorset.name if colorset else project.color_set or "—")
        colorset_label.setProperty("role", "muted")

        self.popup_color = _color_combo(colorset, project.default_popup_marker_color)
        self.playlist_color = _color_combo(colorset, project.default_playlist_marker_color)

        form = QFormLayout()
        form.addRow("Projektname", self.name_edit)
        form.addRow("Produktionsdatum", self.date_edit)
        form.addRow("Notizen", self.notes_edit)
        form.addRow("Color-Set", colorset_label)
        form.addRow("Farbe Popup-Marker", self.popup_color)
        form.addRow("Farbe Playlist-Marker", self.playlist_color)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Projektname fehlt", "Bitte einen Projektnamen eingeben.")
            return

        qdate = self.date_edit.date()
        self._project.name = name
        self._project.production_date = date(qdate.year(), qdate.month(), qdate.day())
        self._project.notes = self.notes_edit.toPlainText()
        self._project.default_popup_marker_color = self.popup_color.currentData()
        self._project.default_playlist_marker_color = self.playlist_color.currentData()
        try:
            self._project.save()
        except Exception as error:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(error))
            return
        self.accept()


class PopupMarkerDialog(QDialog):
    """Free-text marker.

    The timestamp is taken when this dialog opens, not when it is confirmed, so
    typing time never shifts the marker (same behaviour as v3).
    """

    def __init__(self, timestamp_text: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Popup-Marker")
        self.setMinimumWidth(380)

        info = QLabel(f"Zeitstempel: {timestamp_text}")
        info.setProperty("role", "muted")

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Text des Markers")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addWidget(self.text_edit)
        layout.addWidget(buttons)

        self.text_edit.returnPressed.connect(self.accept)
        self.text_edit.setFocus()

    def text(self) -> str:
        return self.text_edit.text().strip()


class PlaylistEditDialog(QDialog):
    """Edit the playlist as plain lines -- one cue per line."""

    def __init__(self, labels: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Playlist bearbeiten")
        self.setMinimumSize(420, 420)

        hint = QLabel("Eine Zeile = ein Playlist-Eintrag.")
        hint.setProperty("role", "muted")

        self.text_edit = QPlainTextEdit("\n".join(labels))

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addWidget(self.text_edit)
        layout.addWidget(buttons)

    def labels(self) -> list[str]:
        return [line.strip() for line in self.text_edit.toPlainText().splitlines() if line.strip()]


class AppSettingsDialog(QDialog):
    """Application-wide preferences (stored outside any project)."""

    LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")

    def __init__(self, settings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Anwendungs-Einstellungen")
        self.setMinimumWidth(480)
        self._settings = settings

        self.dir_edit = QLineEdit(str(settings.get("default_project_dir")))
        browse_button = QPushButton("…")
        browse_button.setFixedWidth(36)
        browse_button.clicked.connect(self._browse)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self.dir_edit)
        dir_row.addWidget(browse_button)

        self.delete_key_check = QCheckBox("Rücktaste löscht den letzten Marker")
        self.delete_key_check.setChecked(bool(settings.get("delete_key_enabled")))

        self.reopen_check = QCheckBox("Zuletzt geöffnetes Projekt beim Start laden")
        self.reopen_check.setChecked(bool(settings.get("reopen_last_project")))

        self.log_combo = QComboBox()
        self.log_combo.addItems(self.LOG_LEVELS)
        current_level = str(settings.get("log_level", "INFO")).upper()
        if current_level in self.LOG_LEVELS:
            self.log_combo.setCurrentText(current_level)

        warning = QLabel("Die Rücktasten-Funktion ist standardmäßig aus, damit ein versehentlicher "
                         "Tastendruck während einer Show keinen Marker entfernt.")
        warning.setWordWrap(True)
        warning.setProperty("role", "muted")

        form = QFormLayout()
        form.addRow("Standard-Projektordner", dir_row)
        form.addRow("", self.delete_key_check)
        form.addRow("", self.reopen_check)
        form.addRow("Log-Level", self.log_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(warning)
        layout.addWidget(buttons)

    def _browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Standard-Projektordner", self.dir_edit.text())
        if directory:
            self.dir_edit.setText(directory)

    def _accept(self) -> None:
        self._settings.set("default_project_dir", self.dir_edit.text().strip() or str(Path.home()), save=False)
        self._settings.set("delete_key_enabled", self.delete_key_check.isChecked(), save=False)
        self._settings.set("reopen_last_project", self.reopen_check.isChecked(), save=False)
        self._settings.set("log_level", self.log_combo.currentText(), save=True)
        logging.getLogger().setLevel(self.log_combo.currentText())
        self.accept()
