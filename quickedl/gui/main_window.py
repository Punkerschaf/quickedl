"""
Main window of QuickEDL v4.

Layout mirrors the live workflow: compact numbered marker buttons on the left,
the running marker list on the right. Every marker action writes the project file
immediately -- there is no unsaved state to lose.

Hotkeys are handled through an application-wide event filter rather than
``keyPressEvent``: focused buttons and text fields consume key presses before they
would ever reach the window, so the filter has to see them first. Because that
filter is global, it is guarded by :meth:`MainWindow.hotkey_state`, and the current
state is always shown in the status bar.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .. import VERSION
from ..core import export_txt, paths
from ..core.colorset import ColorSet, load_colorsets
from ..core.models import DEFAULT_MARKER_LABEL_COUNT
from ..core.project import Project, ProjectError
from ..core.registry import ProjectRegistry
from ..core.settings import Settings
from .dialogs import AppSettingsDialog, PlaylistEditDialog, PopupMarkerDialog, ProjectSettingsDialog
from .project_manager import ProjectManagerDialog
from .widgets import ColorSelectButton, MarkerTable

logger = logging.getLogger(__name__)

TEXT_INPUT_TYPES = (QLineEdit, QPlainTextEdit, QTextEdit)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"QuickEDL {VERSION}")
        self.resize(940, 620)

        self.settings = Settings()
        self.registry = ProjectRegistry()
        self.colorsets = load_colorsets()

        self.project: Project | None = None
        self.playlist_index = 0

        self._build_ui()
        self._build_menu()
        self._update_project_ui()
        self._restore_last_project()

        application = QApplication.instance()
        application.installEventFilter(self)
        application.focusChanged.connect(lambda *_: self._update_hotkey_indicator())
        self._update_hotkey_indicator()

    # -------------------------------------------------------------- ui setup

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # ---- left: project info + marker controls
        left = QVBoxLayout()
        left.setSpacing(4)

        self.project_name_label = QLabel("Kein Projekt geladen")
        self.project_name_label.setProperty("role", "title")
        self.project_meta_label = QLabel("")
        self.project_meta_label.setProperty("role", "muted")

        left.addWidget(self.project_name_label)
        left.addWidget(self.project_meta_label)

        # marker buttons: number only, the text lives in the edit field next to it
        marker_box = QGroupBox("Marker")
        marker_grid = QGridLayout(marker_box)
        marker_grid.setContentsMargins(6, 4, 6, 6)
        marker_grid.setHorizontalSpacing(4)
        marker_grid.setVerticalSpacing(3)
        marker_grid.setColumnStretch(1, 1)

        self.marker_buttons: list[QPushButton] = []
        self.marker_edits: list[QLineEdit] = []
        self.marker_colors: list[ColorSelectButton] = []

        for index in range(1, DEFAULT_MARKER_LABEL_COUNT + 1):
            button = QPushButton(str(index))
            button.setProperty("role", "marker")
            button.setFixedWidth(30)
            # Never take focus: otherwise the space bar would "click" this button
            # instead of opening the popup marker.
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(lambda _checked=False, i=index: self.add_label_marker(i))

            edit = QLineEdit()
            edit.setPlaceholderText(f"Label {index}")
            edit.editingFinished.connect(lambda i=index: self._on_label_editing_finished(i))
            edit.returnPressed.connect(edit.clearFocus)

            color_button = ColorSelectButton()
            color_button.setFocusPolicy(Qt.NoFocus)
            color_button.colorChanged.connect(lambda color_id, i=index: self._on_label_color_changed(i, color_id))

            row = index - 1
            marker_grid.addWidget(button, row, 0)
            marker_grid.addWidget(edit, row, 1)
            marker_grid.addWidget(color_button, row, 2)

            self.marker_buttons.append(button)
            self.marker_edits.append(edit)
            self.marker_colors.append(color_button)

        left.addWidget(marker_box)

        # extra marker actions
        actions_box = QGroupBox("Weitere Marker")
        actions_layout = QHBoxLayout(actions_box)
        actions_layout.setContentsMargins(6, 4, 6, 6)
        actions_layout.setSpacing(4)

        self.popup_button = QPushButton("Popup  (Leertaste)")
        self.popup_button.setFocusPolicy(Qt.NoFocus)
        self.popup_button.clicked.connect(self.add_popup_marker)
        actions_layout.addWidget(self.popup_button)

        self.separator_button = QPushButton("Trennlinie  (0)")
        self.separator_button.setFocusPolicy(Qt.NoFocus)
        self.separator_button.clicked.connect(self.add_separator)
        actions_layout.addWidget(self.separator_button)

        left.addWidget(actions_box)

        # playlist
        playlist_box = QGroupBox("Playlist")
        playlist_layout = QVBoxLayout(playlist_box)
        playlist_layout.setContentsMargins(6, 4, 6, 6)
        playlist_layout.setSpacing(3)

        self.playlist_label = QLabel("—")
        self.playlist_label.setProperty("role", "playlist")
        self.playlist_label.setWordWrap(True)
        playlist_layout.addWidget(self.playlist_label)

        self.playlist_position_label = QLabel("")
        self.playlist_position_label.setProperty("role", "muted")
        playlist_layout.addWidget(self.playlist_position_label)

        playlist_buttons = QHBoxLayout()
        playlist_buttons.setSpacing(4)
        self.playlist_prev_button = QPushButton("◀")
        self.playlist_prev_button.setFixedWidth(34)
        self.playlist_prev_button.setFocusPolicy(Qt.NoFocus)
        self.playlist_prev_button.clicked.connect(lambda: self.step_playlist(-1))
        self.playlist_next_button = QPushButton("▶")
        self.playlist_next_button.setFixedWidth(34)
        self.playlist_next_button.setFocusPolicy(Qt.NoFocus)
        self.playlist_next_button.clicked.connect(lambda: self.step_playlist(1))
        self.playlist_trigger_button = QPushButton("Playlist-Marker  (P)")
        self.playlist_trigger_button.setProperty("role", "primary")
        self.playlist_trigger_button.setFocusPolicy(Qt.NoFocus)
        self.playlist_trigger_button.clicked.connect(self.add_playlist_marker)

        playlist_buttons.addWidget(self.playlist_prev_button)
        playlist_buttons.addWidget(self.playlist_trigger_button)
        playlist_buttons.addWidget(self.playlist_next_button)
        playlist_layout.addLayout(playlist_buttons)

        left.addWidget(playlist_box)
        left.addStretch()

        left_container = QWidget()
        left_container.setLayout(left)
        left_container.setMaximumWidth(430)

        # ---- right: marker list
        right = QVBoxLayout()
        right.setSpacing(4)
        right.addWidget(QLabel("Marker-Liste"))
        self.marker_table = MarkerTable()
        self.marker_table.setMinimumWidth(360)
        # The table must not swallow the hotkeys via its own keyboard search.
        self.marker_table.setFocusPolicy(Qt.NoFocus)
        right.addWidget(self.marker_table)

        self.delete_button = QPushButton("Letzten Marker löschen")
        self.delete_button.setProperty("role", "danger")
        self.delete_button.setFocusPolicy(Qt.NoFocus)
        self.delete_button.clicked.connect(self.delete_last_marker)
        right.addWidget(self.delete_button)

        root.addWidget(left_container, 3)
        root.addLayout(right, 4)

        self.hotkey_indicator = QLabel()
        self.statusBar().addPermanentWidget(self.hotkey_indicator)
        self.statusBar().showMessage("Bereit.")

    def _build_menu(self) -> None:
        project_menu = self.menuBar().addMenu("&Projekt")

        manager_action = QAction("Projekt-Manager…", self)
        manager_action.setShortcut(QKeySequence("Ctrl+O"))
        manager_action.triggered.connect(self.open_project_manager)
        project_menu.addAction(manager_action)

        self.project_settings_action = QAction("Projekt-Einstellungen…", self)
        self.project_settings_action.triggered.connect(self.open_project_settings)
        project_menu.addAction(self.project_settings_action)

        project_menu.addSeparator()

        self.playlist_action = QAction("Playlist bearbeiten…", self)
        self.playlist_action.triggered.connect(self.edit_playlist)
        project_menu.addAction(self.playlist_action)

        project_menu.addSeparator()

        self.export_action = QAction("Als TXT exportieren…", self)
        self.export_action.triggered.connect(self.export_txt)
        project_menu.addAction(self.export_action)

        project_menu.addSeparator()

        quit_action = QAction("Beenden", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        project_menu.addAction(quit_action)

        app_menu = self.menuBar().addMenu("&Einstellungen")
        settings_action = QAction("Anwendungs-Einstellungen…", self)
        settings_action.triggered.connect(self.open_app_settings)
        app_menu.addAction(settings_action)

        help_menu = self.menuBar().addMenu("&Hilfe")
        about_action = QAction("Über QuickEDL", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # --------------------------------------------------------------- hotkeys

    def hotkey_state(self) -> tuple[bool, str]:
        """Whether hotkeys currently fire, plus the reason when they do not."""
        if self.project is None:
            return False, "kein Projekt"
        if QApplication.activeModalWidget() is not None:
            return False, "Dialog offen"
        if not self.isActiveWindow():
            return False, "Fenster nicht aktiv"
        if isinstance(QApplication.focusWidget(), TEXT_INPUT_TYPES):
            return False, "Texteingabe"
        return True, ""

    def _update_hotkey_indicator(self) -> None:
        active, reason = self.hotkey_state()
        self.hotkey_indicator.setText("● Hotkeys aktiv" if active else f"○ Hotkeys aus ({reason})")
        self.hotkey_indicator.setProperty("role", "hotkeys-on" if active else "hotkeys-off")
        self.hotkey_indicator.setToolTip(
            "1–9 Marker · 0 Trennlinie · Leertaste Popup · P Playlist · ←/→ Playlist blättern"
            if active
            else f"Hotkeys sind deaktiviert: {reason}"
        )
        # re-apply the stylesheet so the changed role property takes effect
        self.hotkey_indicator.style().unpolish(self.hotkey_indicator)
        self.hotkey_indicator.style().polish(self.hotkey_indicator)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.KeyPress:
            # Escape always releases a label field, so hotkeys become available again.
            if event.key() == Qt.Key_Escape:
                focus = QApplication.focusWidget()
                if focus in self.marker_edits:
                    focus.clearFocus()
                    return True

            active, _ = self.hotkey_state()
            if active and self._handle_hotkey(event):
                return True
        return super().eventFilter(obj, event)

    def _handle_hotkey(self, event) -> bool:
        """Run the action bound to ``event``. Returns True when it was consumed."""
        if event.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            return False

        key = event.key()

        if Qt.Key_1 <= key <= Qt.Key_9:
            self.add_label_marker(key - Qt.Key_0)
            return True
        if key == Qt.Key_0:
            self.add_separator()
            return True
        if key == Qt.Key_Space:
            self.add_popup_marker()
            return True
        if key == Qt.Key_P:
            self.add_playlist_marker()
            return True
        if key == Qt.Key_Left:
            self.step_playlist(-1)
            return True
        if key == Qt.Key_Right:
            self.step_playlist(1)
            return True
        if key == Qt.Key_Backspace and self.settings.get("delete_key_enabled", False):
            self.delete_last_marker()
            return True
        return False

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.ActivationChange:
            self._update_hotkey_indicator()

    def mousePressEvent(self, event) -> None:
        # Clicking the window background leaves a label field, re-arming hotkeys.
        focus = QApplication.focusWidget()
        if isinstance(focus, TEXT_INPUT_TYPES):
            focus.clearFocus()
        super().mousePressEvent(event)

    # ----------------------------------------------------------- project state

    @property
    def colorset(self) -> ColorSet | None:
        if self.project is None:
            return None
        return self.colorsets.get(self.project.color_set)

    def _restore_last_project(self) -> None:
        if not self.settings.get("reopen_last_project", True):
            return
        last = self.settings.get("last_project")
        if not last or not Path(last).is_file():
            return
        try:
            self.load_project(Project.load(last))
        except ProjectError as error:
            logger.warning("Could not reopen last project: %s", error)

    def load_project(self, project: Project) -> None:
        self.project = project
        self.playlist_index = 0
        project.ensure_marker_label_count()
        self.registry.add(project.path, project.name)
        self.settings.set("last_project", str(project.path))
        self._update_project_ui()
        self.statusBar().showMessage(f"Projekt geladen: {project.path}")

    def _update_project_ui(self) -> None:
        has_project = self.project is not None

        for widget in (
            *self.marker_buttons,
            *self.marker_edits,
            *self.marker_colors,
            self.popup_button,
            self.separator_button,
            self.playlist_trigger_button,
            self.playlist_prev_button,
            self.playlist_next_button,
        ):
            widget.setEnabled(has_project)

        self.project_settings_action.setEnabled(has_project)
        self.playlist_action.setEnabled(has_project)
        self.export_action.setEnabled(has_project)
        self.delete_button.setEnabled(has_project and self.settings.get("delete_key_enabled", False))

        if not has_project:
            self.project_name_label.setText("Kein Projekt geladen")
            self.project_meta_label.setText("Projekt-Manager öffnen mit Strg+O")
            self.marker_table.refresh([], None)
            self._update_playlist_ui()
            self._update_hotkey_indicator()
            return

        project = self.project
        colorset = self.colorset

        self.project_name_label.setText(project.name)
        date_text = project.production_date.strftime("%d.%m.%Y") if project.production_date else "kein Datum"
        colorset_name = colorset.name if colorset else f"{project.color_set} (unbekannt)"
        file_name = project.path.name if project.path else "—"
        self.project_meta_label.setText(f"{date_text}  ·  {colorset_name}  ·  {file_name}")
        self.project_meta_label.setToolTip(str(project.path) if project.path else "")

        for index in range(1, DEFAULT_MARKER_LABEL_COUNT + 1):
            marker_label = project.marker_label(index)
            edit = self.marker_edits[index - 1]
            color_button = self.marker_colors[index - 1]

            edit.blockSignals(True)
            edit.setText(marker_label.label if marker_label else "")
            edit.blockSignals(False)

            color_button.blockSignals(True)
            color_button.set_colorset(colorset)
            color_button.set_color_id(marker_label.color if marker_label else None)
            color_button.blockSignals(False)

            self.marker_buttons[index - 1].setToolTip(
                f"Marker {index}: {marker_label.label}" if marker_label and marker_label.label
                else f"Marker {index}"
            )

        self.marker_table.refresh(project.markers, colorset)
        self._update_playlist_ui()
        self._update_hotkey_indicator()

        if colorset is None and project.color_set:
            self.statusBar().showMessage(
                f"Achtung: Color-Set '{project.color_set}' wurde nicht gefunden. Farben sind deaktiviert."
            )

    def _update_playlist_ui(self) -> None:
        if not self.project or not self.project.playlist:
            self.playlist_label.setText("—")
            self.playlist_position_label.setText("Keine Playlist hinterlegt.")
            self.playlist_trigger_button.setEnabled(False)
            return

        entries = self.project.playlist_labels
        self.playlist_index = max(0, min(self.playlist_index, len(entries) - 1))
        self.playlist_label.setText(entries[self.playlist_index])
        self.playlist_position_label.setText(f"Eintrag {self.playlist_index + 1} von {len(entries)}")
        self.playlist_trigger_button.setEnabled(True)

    # ----------------------------------------------------------- marker actions

    def _require_project(self) -> Project | None:
        if self.project is None:
            self.statusBar().showMessage("Kein Projekt geladen.")
            return None
        return self.project

    def _handle_project_error(self, error: Exception) -> None:
        logger.error("Project operation failed: %s", error)
        QMessageBox.critical(self, "Speichern fehlgeschlagen", str(error))
        self.statusBar().showMessage("Fehler beim Speichern -- siehe Meldung.")

    def add_label_marker(self, index: int) -> None:
        project = self._require_project()
        if project is None:
            return
        try:
            marker = project.add_label_marker(index)
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self._after_marker_added(marker.label)

    def add_popup_marker(self) -> None:
        project = self._require_project()
        if project is None:
            return

        # Timestamp is captured before the dialog opens, so typing time does not shift the marker.
        timestamp = datetime.now()
        dialog = PopupMarkerDialog(timestamp.strftime("%H:%M:%S"), self)
        accepted = dialog.exec() == QDialog.Accepted
        self._update_hotkey_indicator()

        if not accepted:
            self.statusBar().showMessage("Popup-Marker abgebrochen.")
            return

        text = dialog.text()
        if not text:
            self.statusBar().showMessage("Popup-Marker ohne Text verworfen.")
            return

        try:
            project.add_popup_marker(text, created_at=timestamp)
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self._after_marker_added(text)

    def add_playlist_marker(self) -> None:
        project = self._require_project()
        if project is None or not project.playlist:
            return

        entries = project.playlist_labels
        text = entries[self.playlist_index]
        try:
            project.add_playlist_marker(text)
        except ProjectError as error:
            self._handle_project_error(error)
            return

        if self.playlist_index < len(entries) - 1:
            self.playlist_index += 1
        self._after_marker_added(text)

    def add_separator(self) -> None:
        project = self._require_project()
        if project is None:
            return
        try:
            project.add_separator()
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self._after_marker_added("Trennlinie")

    def delete_last_marker(self) -> None:
        project = self._require_project()
        if project is None or not project.markers:
            return
        try:
            marker = project.delete_last_marker()
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self.marker_table.refresh(project.markers, self.colorset)
        label = "Trennlinie" if marker and marker.is_separator else (marker.label if marker else "")
        self.statusBar().showMessage(f"Marker gelöscht: {label}")

    def _after_marker_added(self, label: str) -> None:
        assert self.project is not None
        self.marker_table.refresh(self.project.markers, self.colorset)
        self._update_playlist_ui()
        self.statusBar().showMessage(f"{datetime.now().strftime('%H:%M:%S')}  Marker gesetzt: {label}")

    def step_playlist(self, delta: int) -> None:
        if not self.project or not self.project.playlist:
            return
        self.playlist_index = max(0, min(self.playlist_index + delta, len(self.project.playlist) - 1))
        self._update_playlist_ui()

    # ------------------------------------------------------------ label edits

    def _on_label_editing_finished(self, index: int) -> None:
        if self.project is None:
            return
        text = self.marker_edits[index - 1].text()
        marker_label = self.project.marker_label(index)
        if marker_label is not None and marker_label.label == text:
            return
        try:
            self.project.set_marker_label(index, label=text)
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self.marker_buttons[index - 1].setToolTip(f"Marker {index}: {text}" if text else f"Marker {index}")

    def _on_label_color_changed(self, index: int, color_id: str | None) -> None:
        if self.project is None:
            return
        try:
            self.project.set_marker_label(index, color=color_id, update_color=True)
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self.statusBar().showMessage(
            f"Farbe für Label {index} gesetzt. Bereits gesetzte Marker behalten ihre Farbe."
        )

    # ---------------------------------------------------------------- dialogs

    def open_project_manager(self) -> None:
        default_dir = Path(self.settings.get("default_project_dir", str(Path.home())))
        dialog = ProjectManagerDialog(self.registry, self.colorsets, default_dir, self)
        accepted = dialog.exec() == QDialog.Accepted
        if accepted and dialog.selected_project:
            self.load_project(dialog.selected_project)
        self._update_hotkey_indicator()

    def open_project_settings(self) -> None:
        project = self._require_project()
        if project is None:
            return
        dialog = ProjectSettingsDialog(project, self.colorset, self)
        if dialog.exec() == QDialog.Accepted:
            self.registry.add(project.path, project.name, touch=False)
            self._update_project_ui()
        self._update_hotkey_indicator()

    def open_app_settings(self) -> None:
        dialog = AppSettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.Accepted:
            self._update_project_ui()
        self._update_hotkey_indicator()

    def edit_playlist(self) -> None:
        project = self._require_project()
        if project is None:
            return
        dialog = PlaylistEditDialog(project.playlist_labels, self)
        accepted = dialog.exec() == QDialog.Accepted
        self._update_hotkey_indicator()
        if not accepted:
            return
        try:
            project.set_playlist(dialog.labels())
        except ProjectError as error:
            self._handle_project_error(error)
            return
        self.playlist_index = 0
        self._update_playlist_ui()

    def export_txt(self) -> None:
        project = self._require_project()
        if project is None:
            return

        suggested = str(project.path.with_suffix(".txt")) if project.path else f"{project.name}.txt"
        file_path, _ = QFileDialog.getSaveFileName(self, "Als TXT exportieren", suggested, "Textdateien (*.txt)")
        self._update_hotkey_indicator()
        if not file_path:
            return
        try:
            export_txt.export_project(project, file_path)
        except OSError as error:
            QMessageBox.critical(self, "Export fehlgeschlagen", str(error))
            return
        self.statusBar().showMessage(f"TXT exportiert: {file_path}")

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "Über QuickEDL",
            f"<b>QuickEDL {VERSION}</b><br><br>"
            "Zeitgestempelte Marker-Protokollierung für Live-Produktionen.<br>"
            "GPLv3 · <a href='https://github.com/Punkerschaf/quickedl'>github.com/Punkerschaf/quickedl</a>"
            f"<br><br>Einstellungen: {paths.USER_DATA_DIR}",
        )
