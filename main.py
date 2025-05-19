import os
import subprocess
import sys
import threading
import tkinter as tk
import json
import requests

from netpulsegui import NetPulseGUI

CURRENT_VERSION = "1.4.0"
RELEASE_JSON_URL = (
    "https://raw.githubusercontent.com/kyywes/netpulse/main/release.json"
)


def is_newer_version(remote: str, current: str) -> bool:
    """Compare semantic versions come '1.4.2' > '1.4.0'."""
    try:
        remote_parts = tuple(int(p) for p in remote.split("."))
        current_parts = tuple(int(p) for p in current.split("."))
        return remote_parts > current_parts
    except ValueError:
        # Fallback a confronto stringhe se i numeri non sono parsabili
        return remote > current


def show_splash(on_finish: callable) -> None:
    splash = tk.Tk()
    splash.overrideredirect(True)

    # Centra sullo schermo
    width, height = 400, 250
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    pos_x = (sw - width) // 2
    pos_y = (sh - height) // 2
    splash.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    splash.configure(bg="#1e1e1e")

    tk.Label(
        splash,
        text="NetPulse",
        font=("Segoe UI", 28, "bold"),
        fg="#4CAF50",
        bg="#1e1e1e",
    ).pack(pady=(50, 10))

    tk.Label(
        splash,
        text="Caricamento...",
        font=("Segoe UI", 12),
        fg="#dcdcdc",
        bg="#1e1e1e",
    ).pack()

    progress = tk.Canvas(
        splash, width=200, height=10, bg="#2a2a2a", highlightthickness=0
    )
    bar = progress.create_rectangle(0, 0, 0, 10, fill="#4CAF50")
    progress.pack(pady=20)

    # Anima la barra
    for width_step in range(0, 201, 4):
        # dopo delay ms chiama progress.coords(bar, 0,0,width_step,10)
        splash.after(width_step * 4, progress.coords, bar, 0, 0, width_step, 10)

    # al termine, prima chiudo splash poi chiamo on_finish
    def finish():
        splash.destroy()
        on_finish()

    splash.after(1000, finish)
    splash.mainloop()


def check_for_updates(current_version: str, on_ready: callable) -> None:
    def updater():
        try:
            resp = requests.get(RELEASE_JSON_URL, timeout=5)
            resp.raise_for_status()
            release = resp.json()

            remote_version = release.get("version", "")
            if is_newer_version(remote_version, current_version):
                script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                for f in release.get("files", []):
                    name = f.get("name")
                    url = f.get("url")
                    if not name or not url:
                        continue
                    file_resp = requests.get(url, timeout=5)
                    file_resp.raise_for_status()
                    path = os.path.join(script_dir, name)
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w", encoding="utf-8") as fd:
                        fd.write(file_resp.text)

                # Se lanciato da .exe, rilancio main.py aggiornato
                if os.path.basename(sys.argv[0]) != "main.py":
                    subprocess.Popen(
                        [sys.executable, os.path.join(script_dir, "main.py")],
                        cwd=script_dir,
                    )
                    sys.exit(0)
        except (requests.RequestException, json.JSONDecodeError, OSError) as err:
            print(f"[Updater] update check failed: {err}")
        finally:
            on_ready()

    threading.Thread(target=updater, daemon=True).start()


def launch_gui() -> None:
    root = tk.Tk()
    NetPulseGUI(root)   # non è necessario salvare in variabile
    root.mainloop()


if __name__ == "__main__":
    check_for_updates(CURRENT_VERSION, lambda: show_splash(launch_gui))
