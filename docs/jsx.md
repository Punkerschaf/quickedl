# JSX Export

Unlikely, Adobe do not allow to execute Extend Scripts directly inside the application, nor it has a universal import for markers. The workaround use Adobe's ExtendScript Debugger plugin for VSCode and let it execute the generated JSX script.

## Installation
- Install Visual Studio Code (VS Code) on the same system as *Adobe Premiere Pro*.
- Install the ExtendScript Debugger extension for VS Code. (Click on the Extensions icon in the Activity Bar on the left side of the window, search for the extension and click "install").
<img src="../docs/assets/extendscript-debugger-extension.png" alt="Adobe ExtendScript Debugger extension for VSCode" style="width:50%;" />

- There is no need for further setup

> [!NOTE]
> Under macOS on Apple Silicon Chip VS Code has to be started with Rosetta 2 to work with ExtendScript Debugger.
> Navigate to your application folder, find VS Code and open "Get Info" in it's context menu (cmd+I). Check "Open with Rosetta".

## Usage
Sequence markers in *Premiere Pro* are relative to the sequence start and not bound to a timecode. This means QuickEDL needs to know, which timecode your sequence begins, to calculate the correct offset for each marker.

- **Premiere:** Set your sequence start timecode to first (or slightly before) the TC of your first footage (timeline hamburger menu: set start timecode).
For example: Footage starts at 19:58:00:00, set sequence start to 19:57:00:00 and sync your footage to sequence.

- **QuickEDL:** In JSX export dialoge set the sequence start timecode to the same value as in Premiere Pro. After exporting, the JSX file is located in the directory of the edl file.

> [!IMPORTANT]
> Premiere Pro has to be opend with the correct sequence loaded in the timeline.

- **VS Code:** Open the JSX file in VS Code (or just drag and drop the file in an empty window of VS Code).
In the bottom info bar click on `evaluate script` und choose the used version of *Premiere Pro*. Alternativly you can hit F5 and choose *Extendscript* as debugger.