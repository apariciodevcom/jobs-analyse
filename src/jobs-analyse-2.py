import os
import sys
import pandas as pd

# Pfadkonfiguration für utils
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
TEST_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "test"))
sys.path.append(TEST_VERZEICHNIS)
from utils import clean_text, get_logger

logger = get_logger("jobs-analyse-2")

# -----------------------------
# Konfigurierbare Schlüsselwörter
# -----------------------------
LEVEL_STICHWÖRTER = ["praktikum", "intern", "junior", "senior"]
AUSSCHLUSS_TITEL = ["ceo", "chief executive", "geschäftsführer", "director", "teamleitung", "leiter/in", "head of"]
AUSSCHLUSS_STICHWÖRTER = ["reinigung", "verkauf", "stapler", "pflege"]
TECH_STICHWÖRTER = ["python", "sql", "sap", "excel", "r", "tableau", "power bi", "cloud", "aws", "azure", "linux"]

ROLLE_MUSTER = {
    "data analyst": "Data Analyst",
    "data analytics": "Data Analyst",
    "entwickler": "Software Engineer",
    "developer": "Software Engineer",
    "software engineer": "Software Engineer",
    "account manager": "Account Manager",
    "key account": "Key Account Manager",
    "pflegefachfrau": "Healthcare Staff",
    "gesundheit": "Healthcare Staff",
    "audit": "Audit / Finance",
    "praktikum informatik": "IT Internship"
}

# -----------------------------
# Neue Funktion zur Rollenerkennung
# -----------------------------
def detect_role_from_titel(titel):
    titel_lower = titel.lower()
    for muster, rolle in ROLLE_MUSTER.items():
        if muster in titel_lower:
            return rolle
    return "Unspecified"

# -----------------------------
# Klassifikation der Jobtitel
# -----------------------------
def klassifiziere_jobtitel(df):
    df = df.copy()
    df["titel_klein"] = df["titel"].str.lower()

    df["ausgeschlossen"] = df["titel_klein"].apply(
        lambda x: any(kw in x for kw in AUSSCHLUSS_TITEL + AUSSCHLUSS_STICHWÖRTER)
    )
    df["hat_tech"] = df["titel_klein"].apply(
        lambda x: any(kw in x for kw in TECH_STICHWÖRTER)
    )
    df["stufe"] = df["titel_klein"].apply(
        lambda x: next((lvl for lvl in LEVEL_STICHWÖRTER if lvl in x), "nicht_zugewiesen")
    )
    df["rolle_detected"] = df["titel"].apply(detect_role_from_titel)

    # Relevanz: entweder (nivel conocido y tech) o rol detectado técnico
    df["relevant"] = (
        (~df["ausgeschlossen"]) &
        (
            (df["stufe"] != "nicht_zugewiesen") & (df["hat_tech"])
            |
            (df["rolle_detected"] != "Unspecified")
        )
    )

    return df

# -----------------------------
# Hauptlogik: Einlesen, Reinigen, Klassifizieren
# -----------------------------
EINGABEDATEI = os.path.join(BASIS_VERZEICHNIS, "..", "data", "jobs_scraped.csv")
AUSGABEDATEI = os.path.join(BASIS_VERZEICHNIS, "..", "data", "output_2.csv")

logger.info("jobs-analyse-2,START,Lese Eingabedatei ein")
daten = pd.read_csv(EINGABEDATEI)
for spalte in ["titel", "firma", "ort", "link"]:
    daten[spalte] = daten[spalte].astype(str).apply(clean_text)

logger.info(f"jobs-analyse-2,INFO,Anzahl gelesener Zeilen: {len(daten)}")
klassifiziert = klassifiziere_jobtitel(daten)
klassifiziert.to_csv(AUSGABEDATEI, index=False, encoding="utf-8")

logger.info(f"jobs-analyse-2,SUCCESS,Speichere klassifizierte Daten in {AUSGABEDATEI}")
print(f"✅ Gespeichert: {AUSGABEDATEI} mit Klassifikationen zu Titel, Rolle & Relevanz.")
