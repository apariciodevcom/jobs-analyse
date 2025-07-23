import os
import sys
import json
import pandas as pd
from math import ceil

# --------------------------
# Pfadkonfiguration
# --------------------------
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
DATEN_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "data"))
ZIEL_VERZEICHNIS = os.path.join(DATEN_VERZEICHNIS, "grupos_fase4")
os.makedirs(ZIEL_VERZEICHNIS, exist_ok=True)

EINGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "results.csv")
AUSGABEDATEI = os.path.join(ZIEL_VERZEICHNIS, "results_con_grupo.csv")
STATUS_DATEI = os.path.join(ZIEL_VERZEICHNIS, "grupo_status.json")

# --------------------------
# Logger
# --------------------------
sys.path.append(os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "test")))
from utils import get_logger

logger = get_logger("jobs-analyse-4")

# --------------------------
# Konfiguration
# --------------------------
GRUPPENGROESSE = 20

# --------------------------
# Hauptlogik
# --------------------------
def vorbereiten_gruppierte_daten():
    logger.info("jobs-analyse-4,START,Beginne Gruppierung der Daten")
    
    if not os.path.exists(EINGABEDATEI):
        logger.error(f"jobs-analyse-4,ERROR,Datei nicht gefunden: {EINGABEDATEI}")
        print(f"❌ Datei nicht gefunden: {EINGABEDATEI}")
        sys.exit(1)

    df = pd.read_csv(EINGABEDATEI)
    df = df.reset_index(drop=True)
    df["grupo_id"] = df.index // GRUPPENGROESSE
    num_gruppen = df["grupo_id"].nunique()
    logger.info(f"jobs-analyse-4,INFO,Anzahl Gruppen: {num_gruppen}")

    # JSON-Statusstruktur vorbereiten
    status = {
        f"grupo_{i}": {
            "estado": "pendiente",
            "num_filas": int((df["grupo_id"] == i).sum())
        }
        for i in range(num_gruppen)
    }

    df.to_csv(AUSGABEDATEI, index=False)
    logger.info(f"jobs-analyse-4,SUCCESS,Daten gespeichert in {AUSGABEDATEI}")

    with open(STATUS_DATEI, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=4, ensure_ascii=False)
    logger.info(f"jobs-analyse-4,SUCCESS,Statusdatei gespeichert in {STATUS_DATEI}")

    print(f"✅ {num_gruppen} Gruppen erstellt und gespeichert unter:\n→ {AUSGABEDATEI}")
    print(f"📄 Gruppenstatus gespeichert in:\n→ {STATUS_DATEI}")

# --------------------------
# Direkter Aufruf
# --------------------------
if __name__ == "__main__":
    vorbereiten_gruppierte_daten()
