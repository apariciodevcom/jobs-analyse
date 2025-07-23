import subprocess
import time
import sys
import os

# --------------------------
# Konfiguration
# --------------------------
SRC_VERZEICHNIS = os.path.join(os.getcwd(), "src")
PYTHON = sys.executable  # Aktuelles Python-Interpreter verwenden

DEBUG_MODUS = "--debug" in sys.argv
MAX_ARG = next((arg for arg in sys.argv if arg.startswith("--max=")), None)
MAX_ANZAHL = MAX_ARG.split("=")[1] if MAX_ARG else None

def ausfuehren(name, script, extra_args=None):
    print(f"\n🔹 [{name}] Starte '{script}' ...")
    start = time.time()

    try:
        befehl = [PYTHON, os.path.join(SRC_VERZEICHNIS, script)]
        if extra_args:
            befehl += extra_args
        subprocess.run(befehl, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Ausführen von {script}: {e}")
        sys.exit(1)

    dauer = time.time() - start
    print(f"✅ Fertig: {script} in {dauer:.2f} Sekunden")

def main():
    gesamt_start = time.time()

    print("🚀 Starte vollständige Pipeline für Jobanalyse ...")
    
    ausfuehren("1/4", "jobs-analyse-1.py")
    ausfuehren("2/4", "jobs-analyse-2.py")
    ausfuehren("3/4", "scraper_jobs_info.py")
    
    nlp_args = []
    if MAX_ANZAHL:
        nlp_args.append(MAX_ARG)
    if DEBUG_MODUS:
        nlp_args.append("--debug")
    ausfuehren("4/4", "jobs-analyse-4.py", extra_args=nlp_args)

    gesamt_dauer = time.time() - gesamt_start
    print(f"\n🎯 Pipeline abgeschlossen in {gesamt_dauer:.2f} Sekunden.")

if __name__ == "__main__":
    main()
