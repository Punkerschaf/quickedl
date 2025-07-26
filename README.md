# QuickEDL
<p align="center">
    <img src="assets/icon_128.png" alt="logo">
</p>

Simple application used at live video production to create a list with timestamps and comments similar to an *Edit Decision List (EDL)*.
Prefilled comments are chosen by button or hotkey and safed with timestamp in a TXT-file.

![screensshot mainwindow](docs/assets/screenshot_main_300alpha.png)

# How it works

## Terminology

***Markerlabels*** are textfields next to the ***marker buttons***. They are used as comment (or label) for the ***markers***.

***Markers*** are entries in the ***EDL-file***, containing the timestamp and the label.

The ***EDL-file*** is a simple text file saved in the project folder.

## Project menu
A project is a folder named as it's project, which contains the *edl-file, markerlabels* and *playlist*. These files are automatically created.

- **New Project**: Creates a new project folder and containing files on the given location.
- **Load Project**: Choose the project folder to load. Project files are scanes automatically.
- **Recent Project**: List of recent opened projects. CLick to load. Number of max. entries is set in the settings. Default is 10.

> [!NOTE]
> For JSX-export from single EDL-files (version 2.2.x and below) it is possible to open them without creating a project. They will be not importet in any way.

## Markerlabels menu
- **Save Markerlabels**: Saves current labels to a external file for some kind of library or compatibility with legacy versions.
- **Load Markerlabels**: Loads a external markerlabels file. If a project is loaded, the labels is imported to the project!
- **Save to defaults**: Saves current labels to the defaults, which are loaded at application startup.
- **Load defaults**: Loads the default markerlabels from the settings folder. If a project is loaded, the labels are imported to the project!
- **Edit playlist**: Opens the playlist window. Have a look to [Playlist marker](#playlist-marker).

# How to use

### popup marker:
If you want to create a marker with costum text one time, use spacebar to open a window and enter a custom text. Return key applies and Esc button will abort the popup marker.
No matter how long you need for writing, timestamp the moment of hitting space bar is used.

### delete last marker:
With the delete button you can delete the last marker. For safety reasons the shortcut (backspace key) for this feature is deactivated by default. You can change this in the settings.

Loading markerlabels from external is used for files from legacy versions. They are imported to the project and replaces the current ones.

## Playlist marker
Playlist is used for marker you only need one time in a show (Song titles for example). The playlist is edited in the text menu. One line is a label. The playlist is also stored in the project.
It is possible to save and load playist (simple `*.txt` file). Loading imports and replaces it to the project.

Once a playlist entry is used by clicking on the `Plst`-Button or hitting `P`, the next item in the playlist is automatically loaded.
You can navigate through the playlist labels using the arrow left and right keys.

# Hotkeys
| Key | Function |
|:---:| --- |
| 1 to 9 | Markerbuttons 1 to 9 |
| 0 | Separator line |
| Space | Popup marker |
| P | Playlist marker |
| Backspace | Delete last marker (deactivated by default) |

# Settings

Settings are stored in a folder `/quickedl` currently located in the users home directory.
The folder contains the settings file, defaults markerlabels and the list recent opened projects.
If there is no settings folder found, the app will load default settings.
In the settings window, you can create a the folder.

### Log File
The logfile is located in the users home directory named quickedl.log. Logfile will be cleared at aplication startup.
The log level can be set in the settings window. Default is 'warning'

# Exporting Marker to Premiere Pro
It is possible to export the edl markers as sequence markers to **Adobe Premiere Pro** via an JSX script.

Unlikely there is still no way to execute them directly in Premiere Pro without useage of (paid) third party software.
But there is a free workaround using *VS Code*:
 
[How to use JSX-Script](docs/jsx.md)
