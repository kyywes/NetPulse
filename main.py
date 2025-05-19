import os
import sys
import subprocess
import tempfile
import shutil
import zipfile
import tkinter as tk
import requests

from netpulsegui import NetPulseGUI

# --- Configurazione per l’auto‐update GitHub (branch main.zip) ---
GITHUB_OWNER    = "kyywes"
GITHUB_REPO     = "NetPulse"
CURRENT_VERSION = "1.4.1"  # ← metti qui la versione che vuoi "iniettare" nella tua app
# URL diretto allo ZIP dell’ultimo commit di main
GITHUB_ZIP_MAIN = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/main.zip"


def is_newer_version(remote: str, current: str) -> bool:
    """Confronto semplice 'semantico' tra due versioni 'x.y.z'."""
    try:
        r = tuple(int(x) for x in remote.split("."))
        c = tuple(int(x) for x in current.split("."))
        return r > c
    except ValueError:
        return remote > current


def github_auto_update():
    """
    Scarica sempre main.zip, controlla se la versione nel file version.txt
    interno allo ZIP è > CURRENT_VERSION, e se sì:
      - estrae
      - sovrascrive
      - rilancia l'app
    """
    try:
        # 1) Scarico lo ZIP
        tmp = tempfile.mkdtemp(prefix="np_upd_")
        zip_path = os.path.join(tmp, "main.zip")
        with requests.get(GITHUB_ZIP_MAIN, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)

        # 2) Estraggo in tmp/<repo>-main
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmp)
        extracted = next(
            os.path.join(tmp, d) for d in os.listdir(tmp)
            if os.path.isdir(os.path.join(tmp, d))
        )

        # 3) Leggo la versione interna (opzionale: se hai un version.txt nello ZIP)
        vk = os.path.join(extracted, "version.txt")
        if os.path.isfile(vk):
            with open(vk, "r") as vf:
                remote_ver = vf.read().strip()
        else:
            # Se non hai version.txt, prendi il tag "main" come sempre più nuovo
            remote_ver = CURRENT_VERSION + ".1"

        if is_newer_version(remote_ver, CURRENT_VERSION):
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            # 4) Sovrascrivo tutti i file
            for name in os.listdir(extracted):
                src = os.path.join(extracted, name)
                dst = os.path.join(app_dir, name)
                if os.path.isdir(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                elif os.path.isfile(dst):
                    os.remove(dst)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            # 5) Rilancio l’app e chiudo
            subprocess.Popen([sys.executable, sys.argv[0]], cwd=app_dir)
            sys.exit(0)

    except Exception as e:
        print(f"[Updater] fallito: {e}")


def show_splash(on_finish: callable) -> None:
    splash = tk.Tk()
    splash.overrideredirect(True)
    w, h = 400, 250
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    splash.configure(bg="#1e1e1e")

    tk.Label(splash, text="NetPulse", font=("Segoe UI", 28, "bold"),
             fg="#4CAF50", bg="#1e1e1e").pack(pady=(50,10))
    tk.Label(splash, text="Caricamento...", font=("Segoe UI",12),
             fg="#dcdcdc", bg="#1e1e1e").pack()

    progress = tk.Canvas(splash, width=200, height=10,
                         bg="#2a2a2a", highlightthickness=0)
    bar = progress.create_rectangle(0,0,0,10, fill="#4CAF50")
    progress.pack(pady=20)

    for step in range(0, 201, 4):
        splash.after(step*4, lambda s=step: progress.coords(bar, 0,0,s,10))  # type: ignore

    def finish():
        splash.destroy()
        on_finish()

    splash.after(1000, finish)  # type: ignore
    splash.mainloop()


def launch_gui() -> None:
    root = tk.Tk()
    NetPulseGUI(root)
    root.mainloop()


def main():
    github_auto_update()        # controlla / scarica / ricarica se serve
    show_splash(launch_gui)     # poi splash e GUI vera

if __name__ == "__main__":
    main()
