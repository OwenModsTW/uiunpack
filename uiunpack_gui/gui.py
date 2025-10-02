#!/usr/bin/env python3

import os
import sys
import threading
import traceback
from tkinter import Tk, StringVar, BooleanVar, ttk, filedialog, messagebox
from typing import List

# Local converter module
from uiunpack_gui.etw_ui_convert import (
    convertUIToXML,
    convertXMLToUI,
    detect_version,
    PY_SUPPORTED_VERSIONS,
    has_ruby,
    has_ruby_nokogiri,
    ruby_ui2xml,
    ruby_xml2ui,
)


class UiUnpackPackApp:
    def __init__(self, root: Tk):
        self.root = root
        root.title("Total War UI Unpack/Pack")
        root.geometry("600x360")

        self.mode = StringVar(value='unpack')  # 'unpack' or 'pack'
        self.input_files = []
        self.output_dir = StringVar(value=os.getcwd())
        self.overwrite = BooleanVar(value=True)

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill='both', expand=True)

        # Mode
        mode_lbl = ttk.Label(frm, text="Mode")
        mode_lbl.grid(row=0, column=0, sticky='w')
        mode_box = ttk.Combobox(frm, values=['unpack (UI → XML)', 'pack (XML → UI)'], state='readonly')
        mode_box.grid(row=0, column=1, sticky='we', padx=8)
        mode_box.current(0)
        mode_box.bind('<<ComboboxSelected>>', lambda e: self._on_mode_change(mode_box))

        # Input files
        in_lbl = ttk.Label(frm, text="Input files")
        in_lbl.grid(row=1, column=0, sticky='w', pady=(12, 0))
        self.in_entry = ttk.Entry(frm)
        self.in_entry.grid(row=1, column=1, sticky='we', padx=8, pady=(12, 0))
        in_btn = ttk.Button(frm, text="Browse Files…", command=self._choose_inputs)
        in_btn.grid(row=1, column=2, sticky='we', pady=(12, 0))

        # Add folder button for batch processing
        folder_btn = ttk.Button(frm, text="Add Folder…", command=self._choose_input_folder)
        folder_btn.grid(row=1, column=3, sticky='we', padx=(8,0), pady=(12, 0))

        # Output dir
        out_lbl = ttk.Label(frm, text="Output folder")
        out_lbl.grid(row=2, column=0, sticky='w', pady=(12, 0))
        out_entry = ttk.Entry(frm, textvariable=self.output_dir)
        out_entry.grid(row=2, column=1, sticky='we', padx=8, pady=(12, 0))
        out_btn = ttk.Button(frm, text="Choose…", command=self._choose_output_dir)
        out_btn.grid(row=2, column=2, sticky='we', pady=(12, 0))

        # Overwrite toggle
        chk = ttk.Checkbutton(frm, text="Overwrite existing files", variable=self.overwrite)
        chk.grid(row=3, column=1, sticky='w', pady=(8, 0))

        # Log
        log_lbl = ttk.Label(frm, text="Log")
        log_lbl.grid(row=4, column=0, sticky='nw', pady=(12, 0))
        self.log = ttk.Treeview(frm, show='tree', height=8)
        self.log.grid(row=4, column=1, columnspan=3, sticky='nsew', pady=(12, 0))

        # Run button
        self.run_btn = ttk.Button(frm, text="Run", command=self._run)
        self.run_btn.grid(row=5, column=3, sticky='e', pady=(16, 0))

        # Layout weights
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(4, weight=1)

    def _on_mode_change(self, box):
        val = box.get()
        self.mode.set('pack' if val.startswith('pack') else 'unpack')
        self._update_in_entry_placeholder()

    def _update_in_entry_placeholder(self):
        self.in_entry.delete(0, 'end')
        if self.input_files:
            self.in_entry.insert(0, "; ".join(self.input_files))
        else:
            self.in_entry.insert(0, "(choose one or more files)")

    def _choose_inputs(self):
        if self.mode.get() == 'unpack':
            types = [("All files", "*.*"), ("UI files", "*.ui")]
        else:
            types = [("All files", "*.*"), ("XML files", "*.xml")]
        files = filedialog.askopenfilenames(title="Select input files", filetypes=types)
        if files:
            self.input_files = list(files)
            self._update_in_entry_placeholder()

    def _choose_input_folder(self):
        d = filedialog.askdirectory(title="Select input folder")
        if not d:
            return
        found = self._scan_folder_for_inputs(d)
        if not found:
            messagebox.showinfo("No files found", "No supported files found in the selected folder.")
            return
        # Merge with any existing selections, keeping order and uniqueness
        existing = set(self.input_files)
        for f in found:
            if f not in existing:
                self.input_files.append(f)
        self._update_in_entry_placeholder()

    def _scan_folder_for_inputs(self, root_dir: str) -> List[str]:
        results: List[str] = []
        for base, _, files in os.walk(root_dir):
            for name in files:
                path = os.path.join(base, name)
                if self.mode.get() == 'pack':
                    if name.lower().endswith('.xml'):
                        results.append(path)
                    continue
                # unpack mode: any file that starts with b'Version' header
                try:
                    with open(path, 'rb') as fh:
                        hdr = fh.read(10)
                    if len(hdr) >= 10 and hdr.startswith(b'Version'):
                        results.append(path)
                except Exception:
                    pass
        return results

    def _choose_output_dir(self):
        d = filedialog.askdirectory(title="Select output folder", initialdir=self.output_dir.get() or os.getcwd())
        if d:
            self.output_dir.set(d)

    def _log(self, msg):
        self.log.insert('', 'end', text=str(msg))
        self.log.see(self.log.get_children()[-1])
        self.root.update_idletasks()

    def _run(self):
        if not self.input_files:
            messagebox.showwarning("No input", "Select at least one input file.")
            return
        outdir = self.output_dir.get()
        if not outdir:
            messagebox.showwarning("No output", "Choose an output folder.")
            return
        os.makedirs(outdir, exist_ok=True)
        self.run_btn.config(state='disabled')
        self._log("Starting…")

        def worker():
            try:
                total = len(self.input_files)
                ruby_ok = has_ruby()
                nokogiri_ok = has_ruby_nokogiri() if ruby_ok else False
                for idx, src in enumerate(self.input_files, start=1):
                    base = os.path.basename(src)
                    name, ext = os.path.splitext(base)
                    if self.mode.get() == 'unpack':
                        dst = os.path.join(outdir, base + '.xml')
                        action = 'UI→XML'
                        ver = detect_version(src)
                        if ver is None:
                            raise Exception(f"Not a UI layout file: {src}")
                        if ver in PY_SUPPORTED_VERSIONS:
                            do = lambda: convertUIToXML(src, dst)
                        elif ruby_ok:
                            do = lambda: ruby_ui2xml(src, dst)
                        else:
                            raise Exception(
                                f"UI version {ver:03d} not supported by built-in converter. Install Ruby to enable fallback."
                            )
                    else:
                        dst = os.path.join(outdir, name)
                        action = 'XML→UI'
                        # Prefer Python if supported by target version in XML, otherwise Ruby+Nokogiri
                        # We read the version from the XML to decide
                        ver = None
                        try:
                            with open(src, 'r', encoding='utf-8') as fh:
                                head = fh.read(4000)
                            import re
                            m = re.search(r"<version>\s*(\d{3})\s*</version>", head)
                            if not m:
                                m = re.search(r"<ui[^>]*version=\"(\d{3})\"", head)
                            if m:
                                ver = int(m.group(1))
                        except Exception:
                            pass
                        # If Ruby is present but Nokogiri is missing, offer to install it once
                        if ruby_ok and not nokogiri_ok:
                            try:
                                if messagebox.askyesno(
                                    "Install Nokogiri",
                                    "Ruby is installed but the Nokogiri gem is missing, which is required for packing.\n\nInstall it now?"
                                ):
                                    import subprocess
                                    self._log("Installing Nokogiri gem...")
                                    subprocess.run(['gem', 'install', 'nokogiri', '--no-document'], check=True)
                                    nokogiri_ok = has_ruby_nokogiri()
                                    if not nokogiri_ok:
                                        raise RuntimeError('Nokogiri still not available after installation')
                                    else:
                                        self._log("Nokogiri installed.")
                            except Exception as ie:
                                self._log(f"Failed to install Nokogiri: {ie}")
                        if ver in PY_SUPPORTED_VERSIONS:
                            do = lambda: convertXMLToUI(src, dst)
                        elif ruby_ok and nokogiri_ok:
                            do = lambda: ruby_xml2ui(src, dst)
                        elif ruby_ok and not nokogiri_ok:
                            raise Exception("Ruby found but Nokogiri gem missing. Install with: gem install nokogiri")
                        else:
                            raise Exception("Install Ruby (and Nokogiri for packing) to handle this XML version.")

                    if os.path.exists(dst) and not self.overwrite.get():
                        self._log(f"[{idx}/{total}] Skip (exists): {dst}")
                        continue

                    self._log(f"[{idx}/{total}] {action}: {src} → {dst}")
                    try:
                        do()
                    except Exception as e:
                        self._log(f"ERROR: {e}")
                        traceback.print_exc()
                        messagebox.showerror("Conversion error", f"Failed on:\n{src}\n\n{e}")
                        break
                else:
                    self._log("Done.")
            finally:
                self.run_btn.config(state='normal')

        threading.Thread(target=worker, daemon=True).start()


def main():
    root = Tk()
    # Use native theme if available
    try:
        style = ttk.Style(root)
        if 'vista' in style.theme_names():
            style.theme_use('vista')
    except Exception:
        pass
    app = UiUnpackPackApp(root)
    app._update_in_entry_placeholder()
    root.mainloop()


if __name__ == '__main__':
    main()
