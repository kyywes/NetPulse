import os
import threading
import csv
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from configparser import ConfigParser
from netpulse_core.cli import NetPulse
from netpulse_gui.theme import apply_github_dark_theme
from netpulse_automate.automate import NetPulseAutomate

class NetPulseGUI:
    def __init__(self, root):
        self.root     = root
        self.netpulse = NetPulse()
        self.automate = NetPulseAutomate()

        self.log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.log_dir, exist_ok=True)

        self.command_var    = tk.StringVar(master=self.root, value="Connect Devices")
        self.param_var      = tk.StringVar(master=self.root, value="")
        self.continuous_var = tk.BooleanVar(master=self.root, value=False)
        self.status_var     = tk.StringVar(master=self.root, value="Pronto.")
        self.stop_event     = threading.Event()
        self.thread         = None

        # frame per UI inline (Data PAI-PL / MCU)
        self.inline_frame = None

        colors = apply_github_dark_theme(self.root)
        self._c = colors

        self.root.title("NetPulse – Network Toolkit")
        self.root.geometry("900x550")
        self.root.resizable(False, False)
        self._build_ui()

        self.root.bind('<Return>', lambda e: self._start_command())

    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=12, pady=6)

        ttk.Label(top, text="Comando:").grid(row=0, column=0, sticky=tk.W)
        combo = ttk.Combobox(
            top,
            textvariable=self.command_var,
            values=[
                "Ping", "Traceroute", "Nslookup", "Subnet Info", "Network Scan",
                "Connect Devices","PAI-PL Version","PAI-PL Logs",
                "Data PAI-PL","Configura MCU"
            ],
            width=22, state="normal"
        )
        combo.grid(row=0, column=1, padx=(4,20))

        ttk.Label(top, text="Parametro:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(top, textvariable=self.param_var, width=20).grid(row=0, column=3, padx=(4,20))

        ttk.Checkbutton(top, text="Ping continuo (-t)", variable=self.continuous_var)\
            .grid(row=0, column=4)

        bf = ttk.Frame(self.root)
        bf.pack(fill=tk.X, padx=12, pady=(0,8))
        for txt, cmd in [
            ("Esegui", self._start_command),
            ("Stop",   self._stop_command),
            ("Pulisci",self._clear_output),
            ("Esporta TXT", self._export_txt),
            ("Esporta CSV", self._export_csv),
            ("Modifica SSH", self._edit_ssh_config),
        ]:
            ttk.Button(bf, text=txt, command=cmd, width=14).pack(side=tk.LEFT, padx=4)

        self.tree = ttk.Treeview(self.root, columns=("Output",), show="headings")
        self.tree.heading("Output", text="Output", anchor="w")
        self.tree.column("Output", anchor="w")
        self.tree.pack(expand=True, fill="both", padx=12, pady=(0,8))

        self.tree.tag_configure("cmd",     foreground=self._c['fg_cmd'])
        self.tree.tag_configure("success", foreground=self._c['fg_success'])
        self.tree.tag_configure("error",   foreground=self._c['fg_error'])
        self.tree.tag_configure("warning", foreground=self._c['fg_warning'])

        ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)\
            .pack(fill=tk.X, padx=12, pady=(0,4))

        self.progress = ttk.Progressbar(
            self.root,
            mode="indeterminate",
            style="Green.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, padx=12, pady=(0,8))

    def _start_command(self):
        if self.thread and self.thread.is_alive():
            messagebox.showwarning("NetPulse","Comando già in esecuzione.")
            return
        self.stop_event.clear()
        self._clear_output()
        self.status_var.set("Esecuzione in corso…")
        self.progress.start(10)
        if self.inline_frame:
            self.inline_frame.destroy()
            self.inline_frame = None
        self.thread = threading.Thread(target=self._execute_command, daemon=True)
        self.thread.start()

    def _stop_command(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.netpulse.stop_ping()
            self.status_var.set("Stop richiesto…")
        else:
            self.status_var.set("Nessun comando attivo.")

    def _log_open(self, marker, cmd):
        now   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{marker}_{cmd.replace(' ','_')}_{now}.log"
        path  = os.path.join(self.log_dir, fname)
        return open(path,"w",encoding="utf-8"), path

    def _execute_command(self):
        cmd    = self.command_var.get()
        marker = self.param_var.get().strip()
        log_f, log_path = self._log_open(marker, cmd)
        self._insert_line(f"{cmd} @ {marker}", tag="cmd")
        log_f.write(f"{cmd} @ {marker}\n\n")

        try:
            # PING
            if cmd.lower()=="ping":
                def cb(line):
                    self._insert_line(line, tag="warning")
                    log_f.write(line+"\n")
                self.netpulse.ping(marker, count=4,
                                   continuous=self.continuous_var.get(),
                                   callback=cb)
                self._finish(log_f,"Ping completato.",log_path)
                return

            # CONNECT DEVICES
            if cmd=="Connect Devices":
                text = self.netpulse.format_output(self.automate.connect_devices(marker))
                for line in text.splitlines():
                    tag = "error" if "down" in line.lower() else "success"
                    self._insert_line(line, tag=tag)
                    log_f.write(line+"\n")
                self._finish(log_f,"Connect Devices completato.",log_path)
                return

            # PAI-PL VERSION / LOGS
            if cmd in ("PAI-PL Version","PAI-PL Logs"):
                mode = "v" if "Version" in cmd else "s"
                text = self.netpulse.format_output(self.automate.show_pai(marker,mode=mode))
                for line in text.splitlines():
                    tag = "error" if "error" in line.lower() else "success"
                    self._insert_line(line, tag=tag)
                    log_f.write(line+"\n")
                self._finish(log_f,f"{cmd} completato.",log_path)
                return

            # DATA PAI-PL
            if cmd=="Data PAI-PL":
                # mostra stato
                res0 = self.automate.data(marker,new_date=None)
                for role,info in res0["Data PAI-PL"].items():
                    self._insert_line(f"{role}: Current date → {info['current_date']}", tag="success")
                log_f.write(str(res0)+"\n")
                # pannello inline per modificare
                self._show_data_inline(marker, log_f, log_path)
                return

            # CONFIGURA MCU
            if cmd=="Configura MCU":
                # mostra stato MCU attuale
                # (usiamo data() come helper per navig+date; ma in realtà useremmo un comando specifico)
                res0 = self.automate.data(marker,new_date=None)
                for role,info in res0["Data PAI-PL"].items():
                    # info['navigation'] contiene output di cd/ls
                    # info['current_date'] qui usiamo come placeholder per MCU status
                    stato = "Enabled" if "enabled" in info["current_date"].lower() else "Disabled"
                    self._insert_line(f"{role}: MCU is {stato}", tag="success")
                log_f.write(str(res0)+"\n")
                # pannello inline per invertire
                self._show_mcu_inline(marker, log_f, log_path)
                return

            # COMANDO NON VALIDO
            self._insert_line("Comando non valido.", tag="error")
            log_f.write("Comando non valido.\n")

        except Exception as e:
            line = f"Error: {e.__class__.__name__}"
            self._insert_line(line, tag="error")
            log_f.write(line+"\n")

        self._finish(log_f,"Operazione terminata.",log_path)

    def _show_data_inline(self, marker, log_f, log_path):
        self.inline_frame = ttk.Frame(self.root)
        self.inline_frame.pack(fill=tk.X, padx=12, pady=(0,8))
        ttk.Label(self.inline_frame, text="New date (YYYY-MM-DD hh:mm:ss):")\
            .pack(side=tk.LEFT, padx=(0,8))
        entry = ttk.Entry(self.inline_frame, width=20)
        entry.pack(side=tk.LEFT)

        def mantieni():
            self._insert_line("Data unchanged.", tag="warning")
            self.inline_frame.destroy()
            self.inline_frame = None
            self._finish(log_f,"Data unchanged.",log_path)

        def setta():
            new_dt = entry.get().strip()
            res1 = self.automate.data(marker,new_date=new_dt)
            for role,info in res1["Data PAI-PL"].items():
                self._insert_line(f"{role}: set_date → {info['set_date']}", tag="success")
            log_f.write(str(res1)+"\n")
            self.inline_frame.destroy()
            self.inline_frame = None
            self._finish(log_f,"Date updated.",log_path)

        ttk.Button(self.inline_frame, text="Mantieni", command=mantieni).pack(side=tk.LEFT)
        ttk.Button(self.inline_frame, text="Setta",    command=setta)\
            .pack(side=tk.LEFT, padx=(8,0))

    def _show_mcu_inline(self, marker, log_f, log_path):
        self.inline_frame = ttk.Frame(self.root)
        self.inline_frame.pack(fill=tk.X, padx=12, pady=(0,8))
        ttk.Label(self.inline_frame, text="MCU: keep or invert?")\
            .pack(side=tk.LEFT, padx=(0,8))

        # ricava lo stato dal tree: ultima riga
        last = self.tree.get_children()[-1]
        text = self.tree.item(last, 'values')[0]
        current_enabled = "Enabled" in text

        def mantieni():
            self._insert_line("MCU unchanged.", tag="warning")
            self.inline_frame.destroy()
            self.inline_frame = None
            self._finish(log_f,"MCU unchanged.",log_path)

        def inverti():
            action = "disable" if current_enabled else "enable"
            res2 = self.automate.configure_mcu(marker, action)
            for role,out in res2["Configura MCU"].items():
                self._insert_line(f"{role}: {out}", tag="success")
            log_f.write(str(res2)+"\n")
            self.inline_frame.destroy()
            self.inline_frame = None
            self._finish(log_f,"MCU toggled.",log_path)

        ttk.Button(self.inline_frame, text="Mantieni", command=mantieni).pack(side=tk.LEFT)
        ttk.Button(self.inline_frame, text="Inverti",  command=inverti)\
            .pack(side=tk.LEFT, padx=(8,0))

    def _finish(self, log_f, status, log_path):
        log_f.close()
        self._insert_line(f"Log salvato in {log_path}", tag="success")
        self.status_var.set(status)
        self.progress.stop()

    def _insert_line(self, text, tag="success"):
        self.tree.insert("", "end", values=(text,), tags=(tag,))
        self.tree.see(self.tree.get_children()[-1])

    def _clear_output(self):
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Output pulito.")

    def _export_txt(self):
        files = sorted(os.listdir(self.log_dir))
        if not files:
            messagebox.showinfo("Esporta TXT","Nessun log disponibile.")
            return
        path = tk.filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text","*.txt")])
        if not path:
            return
        with open(os.path.join(self.log_dir, files[-1]), "r", encoding="utf-8") as src, \
             open(path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        self.status_var.set(f"Log esportato in: {path}")

    def _export_csv(self):
        files = sorted(os.listdir(self.log_dir))
        if not files:
            messagebox.showinfo("Esporta CSV","Nessun log disponibile.")
            return
        path = tk.filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV","*.csv")])
        if not path:
            return
        with open(os.path.join(self.log_dir, files[-1]), "r", encoding="utf-8") as src, \
             open(path, "w", newline="", encoding="utf-8") as dst:
            writer = csv.writer(dst)
            for line in src:
                if ":" in line:
                    k,v = line.split(":",1)
                    writer.writerow([k.strip(),v.strip()])
                else:
                    writer.writerow([line.strip()])
        self.status_var.set(f"Log CSV salvato in: {path}")

    def _edit_ssh_config(self):
        cfg_path = self.automate.config_path
        cfg = ConfigParser()
        cfg.read(cfg_path)
        if "ssh" not in cfg:
            cfg.add_section("ssh")

        dlg = tk.Toplevel(self.root)
        dlg.title("Modifica SSH")
        dlg.geometry("300x260")
        fields = [("username","User",False),("password","Password",True),
                  ("port","Port",False),("timeout","Timeout (s)",False),
                  ("retries","Retries",False)]
        entries = {}
        for i,(key,label,is_pwd) in enumerate(fields):
            ttk.Label(dlg,text=label+":").grid(row=i,column=0,sticky=tk.W,padx=8,pady=4)
            var = tk.StringVar(value=cfg["ssh"].get(key,""))
            ent = ttk.Entry(dlg,textvariable=var, show="*" if is_pwd else "")
            ent.grid(row=i,column=1,padx=8,pady=4)
            entries[key]=var

        def save():
            if "ssh" not in cfg:
                cfg.add_section("ssh")
            for k,v in entries.items():
                cfg["ssh"][k] = v.get()
            with open(cfg_path,"w",encoding="utf-8") as f:
                cfg.write(f)
            dlg.destroy()
            messagebox.showinfo("Modifica SSH","Salvato. Riavvia l'app per applicare.")

        ttk.Button(dlg,text="Salva",command=save)\
            .grid(row=len(fields),column=0,columnspan=2,pady=12)

if __name__=="__main__":
    root = tk.Tk()
    NetPulseGUI(root)
    root.mainloop()
