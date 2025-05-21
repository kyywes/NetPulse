import os
import sys
import tempfile
import zipfile
import shutil
import requests
import subprocess

# Parametri
GITHUB_ZIP_MAIN = "https://github.com/kyywes/NetPulse/archive/refs/heads/main.zip"
CURRENT_EXE     = os.path.basename(sys.argv[0])  # ad es. "NetPulse.exe"

def is_newer(remote_ver, local_ver):
    try:
        r = tuple(int(x) for x in remote_ver.split("."))
        l = tuple(int(x) for x in local_ver.split("."))
        return r > l
    except:
        return remote_ver > local_ver

def get_local_version():
    here = os.path.dirname(sys.executable)
    vt = os.path.join(here, "version.txt")
    return open(vt).read().strip() if os.path.isfile(vt) else "0.0.0"

def main():
    local_ver = get_local_version()

    # scarica lo zip
    tmpdir  = tempfile.mkdtemp()
    zippath = os.path.join(tmpdir, "main.zip")
    r = requests.get(GITHUB_ZIP_MAIN, stream=True, timeout=10)
    r.raise_for_status()
    with open(zippath, "wb") as f:
        for chunk in r.iter_content(4096):
            f.write(chunk)

    # estrai e leggi version.txt
    with zipfile.ZipFile(zippath, "r") as z:
        z.extractall(tmpdir)
    extracted = next(os.path.join(tmpdir, d)
                     for d in os.listdir(tmpdir)
                     if os.path.isdir(os.path.join(tmpdir, d)))
    remote_vf = os.path.join(extracted, "version.txt")
    remote_ver = open(remote_vf).read().strip() if os.path.isfile(remote_vf) else local_ver

    if is_newer(remote_ver, local_ver):
        # copia tutti i file estratti sulla cartella corrente
        here = os.path.dirname(sys.executable)
        for name in os.listdir(extracted):
            src = os.path.join(extracted, name)
            dst = os.path.join(here, name)
            if os.path.isdir(src):
                if os.path.exists(dst): shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        print(f"Aggiornato da {local_ver} a {remote_ver}")

    # lancia l’app vera
    app_exe = os.path.join(os.path.dirname(sys.executable), CURRENT_EXE)
    subprocess.Popen([app_exe])
    sys.exit(0)

if __name__ == "__main__":
    main()
