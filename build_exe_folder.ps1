Param(
  [string]$Python = "py -3",
  [string]$Entry = "uiunpack_gui/gui.py",
  [switch]$BundleRuby
)

Write-Host "Building one-folder app..."
& cmd /c "$Python -m PyInstaller --noconsole --name uiunpack_folder --add-data `"etwng\ui;etwng/ui`" $Entry"

if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

if ($BundleRuby) {
  Write-Host "Installing Ruby (temporary) via winget..."
  winget install -e --id RubyInstallerTeam.Ruby.3.2 --silent --accept-source-agreements --accept-package-agreements | Out-Null
  $rubyRoots = @(
    "C:\\Ruby32-x64",
    "$env:ProgramFiles\\Ruby32-x64",
    "$env:LOCALAPPDATA\\Programs\\Ruby"
  )
  $found = $null
  foreach ($r in $rubyRoots) { if (Test-Path (Join-Path $r 'bin\ruby.exe')) { $found = $r; break } }
  if (-not $found) { throw "Ruby install not found" }

  $dst = Join-Path (Resolve-Path 'dist/uiunpack_folder') 'ruby'
  Write-Host "Copying Ruby to $dst ..."
  robocopy $found $dst /E /NFL /NDL /NJH /NJS /NC /NS | Out-Null

  # Install nokogiri gem into the bundled Ruby for packing support
  & (Join-Path $dst 'bin\gem.cmd') install nokogiri --no-document | Out-Null
  Write-Host "Bundled Ruby and Nokogiri ready."
}

Write-Host "Done. Run dist/uiunpack_folder/uiunpack_folder.exe"

