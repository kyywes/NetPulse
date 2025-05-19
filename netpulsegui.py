import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import csv

from netpulse import NetPulse
from netpulsetheme import apply_dark_theme

class NetPulseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NetPulse - Network Toolkit")
        apply_dark_theme(self.root)

        # Frame di controllo
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Indirizzo o rete (CIDR):").pack(side=tk.LEFT)
        self.target_entry = ttk.Entry(control_frame, width=30)
        self.target_entry.pack(side=tk.LEFT, padx=(5,10))

        self.ping_button = ttk.Button(control_frame, text="Ping", command=self._start_ping)
        self.ping_button.pack(side=tk.LEFT)
        self.scan_button = ttk.Button(control_frame, text="Scansione", command=self._start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=(5,0))

        # Area di output
        self.output_text = tk.Text(self.root, wrap=tk.NONE, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Barra di stato
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="Pronto")
        self.status_label.pack(side=tk.LEFT)
        ttk.Button(status_frame, text="Pulisci", command=self._clear_output).pack(side=tk.RIGHT, padx=(0,5))
        ttk.Button(status_frame, text="Esporta", command=self._export_output).pack(side=tk.RIGHT)

    def _start_ping(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showwarning("Ping", "Inserisci un indirizzo o un hostname.")
            return
        threading.Thread(target=self._run_ping, args=(target,), daemon=True).start()

    def _run_ping(self, target):
        self._set_status(f"Pinging {target}…")
        np = NetPulse()
        for line, _ in np.ping(target):
            self._append_output(line)
        self._set_status("Ping completato")

    def _start_scan(self):
        cidr = self.target_entry.get().strip()
        if not cidr:
            messagebox.showwarning("Scansione", "Inserisci una rete in formato CIDR.")
            return
        threading.Thread(target=self._run_scan, args=(cidr,), daemon=True).start()

    def _run_scan(self, cidr):
        self._set_status(f"Scansione rete {cidr}…")
        np = NetPulse()
        result = np.scan_network(cidr)
        hosts = result.get("hosts", []) if isinstance(result, dict) else result
        for ip in hosts:
            self._append_output(ip)
        self._set_status("Scansione completata")

    def _append_output(self, line):
        self.output_text.insert(tk.END, line + "\n")
        self.output_text.see(tk.END)
        self.output_text.update()

    def _clear_output(self):
        self.output_text.delete("1.0", tk.END)

    def _export_output(self):
        content = self.output_text.get("1.0", tk.END).strip().splitlines()
        if not content:
            messagebox.showinfo("Esporta", "Nessun contenuto da esportare.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                for row in content:
                    writer.writerow([row])
            messagebox.showinfo("Esporta", f"Output salvato in {path}.")
        except Exception as e:
            messagebox.showerror("Errore esportazione", str(e))

    def _set_status(self, text):
        self.status_label.config(text=text)
