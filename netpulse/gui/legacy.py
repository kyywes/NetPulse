import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import csv

from netpulse import NetPulse
from netpulsetheme import apply_modern_theme
from netpulse_automate import NetPulseAutomate

class NetPulseGUI:
    def __init__(self, root):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_ini   = os.path.join(base_dir, "inventory", "db_config.ini")
        if not os.path.isfile(db_ini):
            messagebox.showerror("Errore", f"Config DB non trovato:\n{db_ini}")
            root.destroy()
            return

        self.root       = root
        self.netpulse   = NetPulse()
        try:
            from netpulse.automation.device_manager import DeviceManager
            self.automate = DeviceManager()
            print("✓ Automation system initialized")
        except Exception as e:
            print(f"Warning: Could not initialize automation: {e}")
            self.automate = None
        self.command_var     = tk.StringVar(value="Ping")
        self.param_var       = tk.StringVar(value="")
        self.continuous_ping = tk.BooleanVar(value=False)
        self.status_var      = tk.StringVar(value="Pronto.")
        self.thread          = None

        apply_modern_theme(self.root)
        self.root.title("NetPulse - Network Toolkit")
        self.root.geometry("860x520")
        self.root.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=12)

        ttk.Label(frame, text="Comando:").grid(row=0, column=0, padx=5)
        self.command_box = ttk.Combobox(
            frame,
            textvariable=self.command_var,
            values=[
                "Ping","Traceroute","Nslookup",
                "Subnet Info","Network Scan",
                "Connect Devices","Backup Config","PAI-PL Version",
                "Data Management","MCU Control","Advanced MCU Config"
            ],
            width=22,
            state="readonly"
        )
        self.command_box.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Parametro:").grid(row=0, column=2, padx=5)
        self.param_entry = ttk.Entry(frame, textvariable=self.param_var, width=30)
        self.param_entry.grid(row=0, column=3)
        self.param_entry.bind("<Return>", lambda e: self._start_command())

        ttk.Checkbutton(
            frame,
            text="Ping continuo (-t)",
            variable=self.continuous_ping
        ).grid(row=0, column=4, padx=8)

        btns = [
            ("Esegui",      self._start_command),
            ("Stop",        self._stop_command),
            ("Pulisci",     self._clear_output),
            ("Esporta TXT", self._export_output),
            ("Esporta CSV", self._export_csv),
        ]
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=6)
        for txt, cmd in btns:
            ttk.Button(btn_frame, text=txt, command=cmd, width=12)\
                .pack(side="left", padx=6)

        self.output_text = tk.Text(
            self.root, wrap="word",
            bg="#202020", fg="#dcdcdc", insertbackground="white",
            font=("Consolas",10), relief="flat", borderwidth=6
        )
        self.output_text.pack(expand=True, fill="both", padx=10, pady=(4,6))
        for tag, color in [("success","#98c379"),("error","#e06c75"),("warning","#e5c07b")]:
            self.output_text.tag_config(tag, foreground=color)

        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var,
            relief="flat", anchor="w"
        )
        self.status_bar.pack(fill="x", padx=10, pady=(0,6))

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0,6))

    def _start_command(self):
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("In esecuzione…")
        self.progress.start(10)
        self.thread = threading.Thread(target=self._execute_command, daemon=True)
        self.thread.start()

    def _stop_command(self):
        self.netpulse.stop_ping()
        self.status_var.set("Comando interrotto.")
        self.progress.stop()

    def _execute_command(self):
        cmd   = self.command_var.get().lower()
        param = self.param_var.get().strip()
        try:
            if cmd == "ping" and self.continuous_ping.get():
                self.netpulse.ping(param, continuous=True, callback=self._live_append)
                self.status_var.set("Ping continuo terminato.")
                return
            elif cmd == "ping":
                result = self.netpulse.ping(param)
            elif cmd == "traceroute":
                result = self.netpulse.traceroute(param)
            elif cmd == "nslookup":
                result = self.netpulse.nslookup(param)
            elif cmd == "subnet info":
                result = self.netpulse.calc_subnet_info(param)
            elif cmd == "network scan":
                result = self.netpulse.scan_network(param)
            elif cmd == "connect devices":
                result = self.automate.connect_devices(param)
            elif cmd == "backup config":
                # Enhanced backup with type selection (default: running)
                backup_type = "running"  # Can be enhanced with UI selection
                result = self.automate.backup_config(param, backup_type)
            elif cmd == "pai-pl version":
                result = self.automate.show_pai_version(param)
            elif cmd == "data management":
                # Parse param for marker and optional date
                parts = param.split("|") if "|" in param else [param]
                marker = parts[0].strip()
                new_date = parts[1].strip() if len(parts) > 1 else None
                result = self.automate.data(marker, new_date)
            elif cmd == "mcu control":
                # Parse param for marker, action, and config file
                parts = param.split("|") if "|" in param else [param]
                marker = parts[0].strip()
                action = parts[1].strip() if len(parts) > 1 else "status"
                config_file = parts[2].strip() if len(parts) > 2 else "CONFIGURATION"
                result = self.automate.mcu(marker, action, config_file)
            elif cmd == "advanced mcu config":
                # Parse param for marker and config updates
                parts = param.split("|") if "|" in param else [param]
                marker = parts[0].strip()
                config_updates = None
                if len(parts) > 1:
                    try:
                        import json
                        config_updates = json.loads(parts[1].strip())
                    except:
                        pass
                result = self.automate.advanced_mcu_config(marker, config_updates)
            else:
                result = {"error": "Comando non valido"}

            out = (self.netpulse.format_output(result)
                   if isinstance(result, dict) else str(result))
            self._fade_in_output(out)
            self.status_var.set("Comando completato.")
        except Exception as e:
            self.output_text.insert(tk.END, f"Errore: {e}\n", "error")
            self.status_var.set("Errore durante l'esecuzione.")
        finally:
            self.progress.stop()

    def _fade_in_output(self, text: str):
        for line in text.splitlines():
            low = line.lower()
            if "up" in low or "200" in low:
                tag = "success"
            elif "down" in low or "error" in low:
                tag = "error"
            else:
                tag = "warning"
            self.output_text.insert(tk.END, line + "\n", tag)
            self.output_text.see(tk.END)
            self.output_text.update()
            time.sleep(0.01)

    def _live_append(self, line: str):
        tag = "error" if "errore" in line.lower() else "success"
        self.output_text.insert(tk.END, line + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.update()

    def _clear_output(self):
        self.output_text.delete("1.0", tk.END)

    def _export_output(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Esporta", "Nessun contenuto da esportare.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files","*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_var.set(f"Output esportato in: {path}")

    def _export_csv(self):
        lines = self.output_text.get("1.0", tk.END).strip().splitlines()
        if not lines:
            messagebox.showinfo("Esporta CSV", "Nessun contenuto da esportare.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files","*.csv")])
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for line in lines:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        writer.writerow([k.strip(), v.strip()])
                    else:
                        writer.writerow([line])
            self.status_var.set(f"Output CSV salvato in: {path}")