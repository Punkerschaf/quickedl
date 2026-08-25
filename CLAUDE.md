# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

QuickEDL is a desktop tool used during live video productions to log a timestamped Edit Decision List (EDL). Operators press hotkeys/buttons to append `HH:MM:SS - label` lines to a plain-text file in real time, then can export those markers to Adobe Premiere Pro.

## Active rewrite: v4.0.0 (this branch)

`v4.0.0-dev` is a from-scratch architectural overhaul: direct Premiere Pro marker creation via Adobe's UXP API (replacing the manual JSX/ExtendScript-Debugger workflow described below), optional DaVinci Resolve support, and a modernized GUI. The agreed direction is to keep Python as the core and move the GUI to PySide6/Qt (see `roadmap.md` for the full plan, phase breakdown, and open decisions before assuming any of the v3.x architecture below still applies to new work).

## Commands

```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r dependencies.txt
python main.py                                       # run the app
python build.py                                       # PyInstaller build via quickedl.spec -> dist/
```

There is no automated test suite in this repository.

## Architecture (current v3.x codebase)

- **No MVC layer.** UI and logic are mixed per file; Tkinter/ttkbootstrap `Toplevel` windows are self-contained classes instantiated ad hoc from `main.py`'s `QuickEDLApp` (e.g. `export_jsx.py::JSXExportWindow`, `settings/settings_window.py`, `projects/newproject.py`, `playlist.py::Playlist`). There is no central router/controller — `main.py` wires everything directly.
- **A "project" is just a folder**, discovered/matched by filename convention rather than a manifest: `{name}_EDL.txt`, `{name}_MARKERLABEL.txt`, `{name}_PLAYLIST.txt` (see `projects/project.py`). There's no index file tying them together.
- **The EDL data model is unstructured, append-only plain text**: each marker is one line, `"%H:%M:%S - <text>"`, parsed elsewhere by naive `" - "` splitting (e.g. `export_jsx.py`). Writes are synchronous immediate appends (`open(path, 'a')`) — this is the app's core reliability guarantee during a live show (nothing to lose on crash) and should not be casually turned into buffered/batched writes.
- **Settings live outside the repo**, in `~/quickedl/settings.yaml` (`settings/settings_manager.py`), separate from per-project files. The log file is `~/quickedl.log`, truncated on every app startup.
- **Premiere Pro integration today is a manual, file-based bridge, not a live connection.** `export_jsx.py` reads the EDL text file and generates a `.jsx` ExtendScript file that computes each marker's offset in seconds (not frames — a `fps` variable is written into the output but unused) relative to a user-entered sequence-start timecode, then calls `sequence.markers.createMarker()`. The user must manually open that file in VS Code with Adobe's ExtendScript Debugger extension and run it against a running Premiere instance (workflow documented in `docs/jsx.md`). This is exactly the workaround the v4.0.0 UXP rewrite (see `roadmap.md`) replaces.
- **Packaging**: `quickedl.spec` (PyInstaller spec, platform-conditional) driven by `build.py`, both at repo root. CI is `.github/workflows/build-executables.yml` (manual `workflow_dispatch` only), building Windows x64 + macOS Intel + macOS Apple Silicon — no Linux target currently, despite a stray `resources/icon_unix.png`.
- **`version.py`** holds the single `VERSION` string referenced by the app title and the build tooling.
