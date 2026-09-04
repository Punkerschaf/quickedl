"""
Project manager window: the central place to list, create, rename, delete and
import projects.

Deleting distinguishes between removing an entry from the list (file stays) and
deleting the file itself, and the destructive variant always asks first.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..core import paths
from ..core.colorset import ColorSet, default_colorset_id
from ..core.migration import MigrationError, find_v3_project, import_v3_project
from ..core.project import Project, ProjectError, suggest_project_path
from ..core.registry import ProjectRegistry, RegistryEntry
from .dialogs import NewProjectDialog

logger = logging.getLogger(__name__)


class ProjectManagerDialog(QDialog):
    """List of known projects plus the actions that operate on them."""

    COLUMNS = ("Name", "Produktionsdatum", "Zuletzt geändert", "Pfad")

    def __init__(
        self,
        registry: ProjectRegistry,
        colorsets: dict[str, ColorSet],
        default_dir: Path,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Projekt-Manager")
        self.setMinimumSize(820, 460)

        self._registry = registry
        self._colorsets = colorsets
        self._default_dir = default_dir
        self.selected_project: Project | None = None

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.doubleClicked.connect(self._open_selected)

        self.hint = QLabel()
        self.hint.setProperty("role", "muted")

        new_button = QPushButton("Neues Projekt")
        new_button.setProperty("role", "primary")
        new_button.clicked.connect(self._new_project)

        open_button = QPushButton("Öffnen")
        open_button.clicked.connect(self._open_selected)

        add_existing_button = QPushButton("Vorhandene Datei hinzufügen…")
        add_existing_button.clicked.connect(self._add_existing)

        import_button = QPushButton("v3-Projekt importieren…")
        import_button.clicked.connect(self._import_v3)

        rename_button = QPushButton("Umbenennen")
        rename_button.clicked.connect(self._rename_selected)

        remove_button = QPushButton("Aus Liste entfernen")
        remove_button.clicked.connect(self._remove_selected)

        delete_button = QPushButton("Datei löschen")
        delete_button.setProperty("role", "danger")
        delete_button.clicked.connect(self._delete_selected)

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.reject)

        actions = QHBoxLayout()
        for button in (new_button, open_button, add_existing_button, import_button):
            actions.addWidget(button)
        actions.addStretch()

        actions2 = QHBoxLayout()
        for button in (rename_button, remove_button, delete_button):
            actions2.addWidget(button)
        actions2.addStretch()
        actions2.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)
        layout.addWidget(self.hint)
        layout.addLayout(actions2)

        self.refresh()

    # ------------------------------------------------------------------ table

    def refresh(self) -> None:
        entries = self._registry.entries
        self.table.setRowCount(len(entries))
        missing = 0

        for row, entry in enumerate(entries):
            production_date = ""
            if entry.exists:
                try:
                    production_date = self._read_production_date(entry.path)
                except ProjectError:
                    production_date = "?"
            else:
                missing += 1

            modified = entry.modified_at
            values = [
                entry.name,
                production_date,
                modified.strftime("%d.%m.%Y %H:%M") if modified else "",
                str(entry.path),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if not entry.exists:
                    item.setForeground(Qt.gray)
                    if column == 0:
                        item.setText(f"{value}  (Datei nicht gefunden)")
                self.table.setItem(row, column, item)

        self.hint.setText(
            f"{len(entries)} Projekt(e)"
            + (f", davon {missing} nicht auffindbar (verschoben oder gelöscht)." if missing else ".")
        )
        if entries:
            self.table.selectRow(0)

    @staticmethod
    def _read_production_date(path: Path) -> str:
        project = Project.load(path)
        return project.production_date.strftime("%d.%m.%Y") if project.production_date else ""

    def _selected_entry(self) -> RegistryEntry | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._registry.entries):
            return None
        return self._registry.entries[row]

    # ---------------------------------------------------------------- actions

    def _new_project(self) -> None:
        dialog = NewProjectDialog(self._colorsets, self._default_dir, self)
        if dialog.exec() == QDialog.Accepted and dialog.project:
            self._registry.add(dialog.project.path, dialog.project.name)
            self.selected_project = dialog.project
            self.accept()

    def _open_selected(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return
        if not entry.exists:
            QMessageBox.warning(
                self,
                "Datei nicht gefunden",
                f"Die Projektdatei existiert nicht mehr:\n{entry.path}\n\n"
                "Sie kann aus der Liste entfernt oder über 'Vorhandene Datei hinzufügen' "
                "neu verknüpft werden.",
            )
            return
        try:
            project = Project.load(entry.path)
        except ProjectError as error:
            QMessageBox.critical(self, "Projekt konnte nicht geladen werden", str(error))
            return
        self._registry.add(project.path, project.name)
        self.selected_project = project
        self.accept()

    def _add_existing(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Projektdatei auswählen",
            str(self._default_dir),
            f"QuickEDL-Projekte (*{paths.PROJECT_FILE_SUFFIX});;Alle Dateien (*)",
        )
        if not file_path:
            return
        try:
            project = Project.load(file_path)
        except ProjectError as error:
            QMessageBox.critical(self, "Projekt konnte nicht geladen werden", str(error))
            return
        self._registry.add(project.path, project.name, touch=False)
        self.refresh()

    def _import_v3(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "v3-Projektordner auswählen", str(self._default_dir)
        )
        if not folder:
            return

        try:
            found = find_v3_project(folder)
        except MigrationError as error:
            QMessageBox.warning(self, "Kein v3-Projekt gefunden", str(error))
            return

        target = suggest_project_path(Path(folder).parent, found.name)
        target_str, _ = QFileDialog.getSaveFileName(
            self,
            "Konvertiertes Projekt speichern unter",
            str(target),
            f"QuickEDL-Projekte (*{paths.PROJECT_FILE_SUFFIX})",
        )
        if not target_str:
            return

        try:
            project = import_v3_project(
                folder,
                target_str,
                color_set=default_colorset_id(self._colorsets),
            )
        except (MigrationError, ProjectError) as error:
            QMessageBox.critical(self, "Import fehlgeschlagen", str(error))
            return

        self._registry.add(project.path, project.name, touch=False)
        self.refresh()
        QMessageBox.information(
            self,
            "Import abgeschlossen",
            f"'{project.name}' wurde importiert:\n"
            f"{len(project.markers)} Marker, {len(project.playlist)} Playlist-Einträge.\n\n"
            "Hinweis: v3 speicherte kein Datum. Die Marker-Daten wurden aus dem Änderungsdatum "
            "der EDL-Datei rekonstruiert und sollten in den Projekt-Einstellungen geprüft werden.",
        )

    def _rename_selected(self) -> None:
        entry = self._selected_entry()
        if entry is None or not entry.exists:
            return

        new_name, ok = QInputDialog.getText(self, "Projekt umbenennen", "Neuer Projektname:", text=entry.name)
        new_name = new_name.strip() if ok else ""
        if not ok or not new_name or new_name == entry.name:
            return

        try:
            project = Project.load(entry.path)
            new_path = suggest_project_path(entry.path.parent, new_name)
            if new_path != entry.path and new_path.exists():
                QMessageBox.warning(self, "Datei existiert", f"{new_path.name} existiert bereits.")
                return

            project.name = new_name
            project.save(new_path)
            if new_path != entry.path:
                entry.path.unlink(missing_ok=True)
        except (ProjectError, OSError) as error:
            QMessageBox.critical(self, "Umbenennen fehlgeschlagen", str(error))
            return

        self._registry.rename(entry.path, new_path, new_name)
        self.refresh()

    def _remove_selected(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return
        self._registry.remove(entry.path)
        self.refresh()

    def _delete_selected(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return

        answer = QMessageBox.question(
            self,
            "Projektdatei löschen",
            f"Die Datei wird endgültig gelöscht:\n{entry.path}\n\n"
            "Das lässt sich nicht rückgängig machen. Fortfahren?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            entry.path.unlink(missing_ok=True)
        except OSError as error:
            QMessageBox.critical(self, "Löschen fehlgeschlagen", str(error))
            return

        self._registry.remove(entry.path)
        self.refresh()
