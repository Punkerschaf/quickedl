# quickEDL
Simple Python app with TKinter-UI for creating simple *Edit Decision Lists* (EDL) with current time as timestamps.

# How it works

 ### Save & Load texts
 For saving and loading the content for the 9 predefined text entries. Just an additional .txt-file.
 It basically reads the first 9 lines of a file. So it's possible to save them into the edl-list itself.

 ### Load file / Create new file
 Loads or creates a new .txt-file where the EDL entries are stored. The current loaded files path is shown below.

 ### Making Entries
 When clicking the buttons or using the number keys 1-9, it writes an edl entry whith the current time and text of the corresponding text field.
 Number Key 0 creates a seperator

 Spacebutton keeps the time in that moment and let's you enter a custom text.
 
 ### Exporting
 Exporting functions are experiments for generating marker files for Adobe Premiere Pro and maybe other NLE applications. They are not functional at the moment but public for test reasons.

- **CMX** or **Sony CMX 3600**: Million years old standard by Sony, which normally doesn't support markers, but only cuts and fades. However there are hints for importing `*COMMENT:` part as markers.

- **FCP7** is an XML based Adobe files containing clip or sequence data. Seems to be the easier way, while there is a section for markers.

# Roadmap
- use tkinter.grid
- Get export working
- change to cooler GUI framework
