import os
import sys
import logging
import subprocess
import time
import pandas as pd
from datetime import timedelta

# ----------------------------
# Konfiguration
# ----------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".."))
LOG_FILE = os.path.join(BASE_DIR, "logs", "main.log")
DATA_DIR = os.path.join(BASE_DIR, "data")
FOLDER_GRUPOS = os.path.join(DATA_DIR, "grupos_fase4")

# ----------------------------
# Logging-Verzeichnis sicherstellen
# ----------------------------
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ----------------------------
# Logging einrichten
# ----------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s,%(name)s,%(levelname)s,%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("JobsAnalyse")

# ----------------------------
# Hilfsfunktionen
# ----------------------------
def run_script(script_name, output_file=None):
    script_path = os.path.join(BASE_DIR, "src", script_name)
    logger.info(f"{script_name},START,Starte Script")
    start = time.time()
    try:
        subprocess.run([sys.executable, script_path], check=True)
        duration = round(time.time() - start, 2)
        logger.info(f"{script_name},SUCCESS,Erfolgreich abgeschlossen")
        logger.info(f"{script_name},INFO,Dauer: {duration} Sekunden")

        if output_file and os.path.exists(output_file):
            try:
                df = pd.read_csv(output_file)
                logger.info(f"{script_name},INFO,Eintraege verarbeitet: {len(df)}")
            except Exception as e:
                logger.warning(f"{script_name},WARN,Konnte Datei nicht lesen: {output_file} ({e})")

    except subprocess.CalledProcessError as e:
        logger.error(f"{script_name},ERROR,Fehler beim Ausführen: {e}")
        sys.exit(1)

# ----------------------------
# Hauptablauf
# ----------------------------
if __name__ == "__main__":
    start_pipeline = time.time()
    logger.info("pipeline,START,Starte Pipeline: Jobs Analyse St. Gallen & Zurich")

    run_script("jobs-analyse-1.py", os.path.join(DATA_DIR, "jobs_scraped.csv"))
    run_script("jobs-analyse-2.py", os.path.join(DATA_DIR, "output_2.csv"))
    run_script("jobs-analyse-3.py", os.path.join(DATA_DIR, "results.csv"))
    run_script("jobs-analyse-4.py", os.path.join(FOLDER_GRUPOS, "results_con_grupo.csv"))
    final_output = os.path.join(FOLDER_GRUPOS, "analyzed_offers_optimized.csv")
    run_script("jobs-analyse-5.py", final_output)

    total_duration = timedelta(seconds=round(time.time() - start_pipeline))
    logger.info("pipeline,SUCCESS,Pipeline abgeschlossen")
    logger.info(f"pipeline,INFO,Gesamtdauer: {str(total_duration)}")

    if os.path.exists(final_output):
        try:
            df_final = pd.read_csv(final_output)
            logger.info(f"pipeline,INFO,Anzahl finaler Angebote: {len(df_final)}")
        except Exception as e:
            logger.warning(f"pipeline,WARN,Konnte finale Datei nicht lesen: {final_output} ({e})")