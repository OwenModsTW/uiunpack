UI Unpack/Pack GUI for Total War UI files

Overview
- Wraps taw/etwng UI converter (Python implementation) with a simple GUI.
- Unpacks `.ui` → `.xml` and repacks `.xml` → `.ui`.

Usage
- Run `py -3 uiunpack_gui/gui.py` to launch the GUI.
- Choose mode: Unpack (UI→XML) or Pack (XML→UI).
- Select one or more input files.
- Pick an output folder.
- Click Run.

Build EXE (Windows)
1) Install Python 3.11+ and pip.
2) Install PyInstaller:
   `py -3 -m pip install pyinstaller`
3) Build:
   `py -3 -m PyInstaller --noconsole --onefile uiunpack_gui/gui.py`
4) The EXE will be at `dist/gui.exe`.

Notes
- Converter code is vendored from `etwng/ui/bin/convert_ui.py` and adapted as a module.
- Supported versions are per upstream: 32, 33, 39, 43, 44, 46, 47, 49, 50, 51, 52, 54.

Troubleshooting pack (XML -> UI)
- For UI versions newer than those listed above (e.g. 086), packing uses the Ruby
  fallback script `etwng/ui/bin/xml2ui` and requires the Ruby `nokogiri` gem.
- If packing fails and the log mentions Nokogiri, install it with:
  `gem install nokogiri`
- Ensure Ruby is available on PATH: `ruby --version` should print a version.
