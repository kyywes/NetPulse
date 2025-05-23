import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import sys
import subprocess
import tempfile
import shutil
import zipfile
import tkinter as tk
import requests

from netpulsegui import NetPulseGUI

# --- auto-update GitHub ---
GITHUB_OWNER    = "kyywes"
GITHUB_REPO     = "NetPulse"
CURRENT_VERSION = "1.4.1"
GITHUB_ZIP_MAIN = (
    f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/"
    "archive/refs/heads/main.zip"
)


def is_newer_version(remote: str, current: str) -> bool:
    """Confronto semantico tra due versioni 'x.y.z'."""
    try:
        r = tuple(int(x) for x in remote.split("."))
        c = tuple(int(x) for x in current.split("."))
        return r > c
    except:
        return remote > current


def github_auto_update():
    """
    Scarica main.zip, legge version.txt e, se rem > cur, sovrascrive
    e rilancia; altrimenti prosegue.
    """
    try:
        tmp = tempfile.mkdtemp(prefix="np_upd_")
        zipp = os.path.join(tmp, "main.zip")
        with requests.get(GITHUB_ZIP_MAIN, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(zipp, "wb") as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)

        with zipfile.ZipFile(zipp, "r") as z:
            z.extractall(tmp)
        extracted = next(
            os.path.join(tmp, d)
            for d in os.listdir(tmp)
            if os.path.isdir(os.path.join(tmp, d))
        )

        vk = os.path.join(extracted, "version.txt")
        if os.path.isfile(vk):
            with open(vk, "r") as vf:
                remote_ver = vf.read().strip()
        else:
            remote_ver = CURRENT_VERSION  # fallback

        if is_newer_version(remote_ver, CURRENT_VERSION):
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
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

            subprocess.Popen([sys.executable, sys.argv[0]], cwd=app_dir)
            sys.exit(0)
    except Exception as e:
        print(f"[Updater] fallito: {e}")


def show_splash():
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

    canvas = tk.Canvas(splash, width=200, height=10,
                       bg="#2a2a2a", highlightthickness=0)
    bar = canvas.create_rectangle(0,0,0,10, fill="#4CAF50")
    canvas.pack(pady=20)
    for i in range(0, 201, 4):
        splash.after(i*4, lambda x=i: canvas.coords(bar, 0,0,x,10))

    splash.after(1000, splash.destroy)
    splash.mainloop()


def launch_gui():
    root = tk.Tk()
    NetPulseGUI(root)
    root.mainloop()


def main():
    github_auto_update()
    show_splash()
    launch_gui()


if __name__ == "__main__":
    main()
