Param(
  [string]$Python = "py -3",
  [string]$Entry = "uiunpack_gui/gui.py"
)

Write-Host "Installing PyInstaller..."
& cmd /c "$Python -m pip install --upgrade pip pyinstaller"

Write-Host "Building single-file EXE..."
$addData1 = "etwng\ui;etwng/ui"
& cmd /c "$Python -m PyInstaller --noconsole --onefile --name uiunpack --add-data `"$addData1`" $Entry"

Write-Host "Done. Check dist/uiunpack.exe"
