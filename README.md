# UI Unpack/Pack Tool for Total War Games

A tool for unpacking and packing Total War UI files (.ui ↔ .xml) using the etwng scripts.

## ⚠️ Antivirus False Positive Warning

**If your antivirus software flags `uiunpack.exe` as a threat, this is a FALSE POSITIVE.**

### Why does this happen?

- This executable is built using PyInstaller, which packages Python scripts into a standalone .exe file
- Antivirus software often flags PyInstaller executables as suspicious because malware authors sometimes use the same tool
- **This is a known issue affecting ALL PyInstaller applications**, not a sign of actual malware

### How to verify this is safe:

1. **Open Source**: This tool uses the open-source [etwng](https://github.com/taw/etwng) scripts created by taw
2. **Scan on VirusTotal**: Upload the .exe to https://www.virustotal.com to see detailed scan results
3. **Use the source code**: Instead of the .exe, you can run the Ruby scripts directly (see below)

### Solutions:

**Option 1: Add to Windows Defender Exclusions**
1. Open Windows Security
2. Go to Virus & threat protection → Manage settings
3. Scroll to Exclusions → Add or remove exclusions
4. Add the `uiunpack.exe` file or folder

**Option 2: Use Ruby Scripts Directly (Recommended)**

Instead of using the .exe, run the original Ruby scripts:

```bash
# Convert UI to XML
ruby etwng/ui/bin/ui2xml input.ui output.xml

# Convert XML to UI
ruby etwng/ui/bin/xml2ui input.xml output.ui
```

**Requirements**: Ruby must be installed on your system
- Download: https://rubyinstaller.org/
- Install the Nokogiri gem: `gem install nokogiri`

## About etwng

This tool uses scripts from the [etwng project](https://github.com/taw/etwng) by taw, which provides tools for modding Total War games. All conversion functionality comes from these well-established, open-source scripts.

## Usage

### GUI Mode
Run `uiunpack.exe` and use the graphical interface to:
- Select mode: Unpack (UI → XML) or Pack (XML → UI)
- Choose input file(s) or folder
- Choose output folder
- Click convert

### Command Line Mode (Ruby)

**Unpack a UI file to XML:**
```bash
ruby etwng/ui/bin/ui2xml path/to/file.ui path/to/output.xml
```

**Pack an XML file to UI:**
```bash
ruby etwng/ui/bin/xml2ui path/to/file.xml path/to/output.ui
```

## Supported Versions

The tool supports UI file versions from Total War games including:
- Empire: Total War
- Napoleon: Total War
- Total War: Shogun 2
- Total War: Rome 2
- Total War: Attila
- And other Total War titles using similar UI formats

## Troubleshooting

### XML Parsing Errors

If you get XML parsing errors when converting XML → UI:
- Your XML file may be corrupted or have mismatched tags
- Validate your XML structure before conversion
- If you unpacked the file yourself, try unpacking again from the original .ui file

### Version Not Supported

Some UI file versions are only supported by the Ruby scripts, not the Python converter. Use the Ruby scripts directly for maximum compatibility.

## Credits

- **etwng scripts**: Created by [taw](https://github.com/taw/etwng)
- **GUI wrapper**: Community contribution for easier access to etwng functionality

## License

The etwng scripts are licensed under their original license. See the etwng repository for details.

## Support

For issues with:
- **UI conversion functionality**: Check the [etwng repository](https://github.com/taw/etwng)
- **This tool**: Create an issue with details about your problem

---

**Remember**: If your antivirus blocks this tool, it's a false positive. You can safely add it to exclusions or use the Ruby scripts directly.
