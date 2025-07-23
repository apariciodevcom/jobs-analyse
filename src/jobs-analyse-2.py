import os
import sys
import pandas as pd

# Pfadkonfiguration für utils
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
TEST_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "test"))
sys.path.append(TEST_VERZEICHNIS)
from utils import clean_text

# -----------------------------
# Konfigurierbare Schlüsselwörter
# -----------------------------
LEVEL_STICHWÖRTER = ["praktikum", "intern", "junior", "senior"]
AUSSCHLUSS_TITEL = ["ceo", "chief executive", "geschäftsführer", "director", "teamleitung", "leiter/in", "head of"]
AUSSCHLUSS_STICHWÖRTER = ["reinigung", "verkauf", "stapler", "pflege"]
TECH_STICHWÖRTER = ["python", "sql", "sap", "excel", "r", "tableau", "power bi", "cloud", "aws", "azure", "linux"]

# -----------------------------
# Klassifikation der Jobtitel
# -----------------------------
def klassifiziere_jobtitel(df):
    df = df.copy()
    df["titel_klein"] = df["titel"].str.lower()

    # Flags setzen
    df["ausgeschlossen"] = df["titel_klein"].apply(lambda x: any(kw in x for kw in AUSSCHLUSS_TITEL + AUSSCHLUSS_STICHWÖRTER))
    df["hat_tech"] = df["titel_klein"].apply(lambda x: any(kw in x for kw in TECH_STICHWÖRTER))
    df["stufe"] = df["titel_klein"].apply(lambda x: next((lvl for lvl in LEVEL_STICHWÖRTER if lvl in x), "nicht_zugewiesen"))

    # Vertragsart klassifizieren
    def klassifiziere_vertrag(ort):
        if isinstance(ort, str):
            ort_klein = ort.lower()
            if "intern" in ort_klein or "praktikum" in ort_klein:
                return "praktikum"
            elif "unlimited" in ort_klein or "unbefristet" in ort_klein:
                return "unbefristet"
            elif "temporary" in ort_klein or "befristet" in ort_klein:
                return "befristet"
            elif "year" in ort_klein or "chf" in ort_klein:
                return "mit_gehaltsangabe"
        return "nicht_zugewiesen"

    df["vertragsart"] = df["ort"].apply(klassifiziere_vertrag)

    # Relevanzflag setzen
    df["relevant"] = (~df["ausgeschlossen"]) & (df["stufe"] != "nicht_zugewiesen") & (df["hat_tech"])

    return df

# -----------------------------
# Hauptlogik: Einlesen, Reinigen, Klassifizieren
# -----------------------------
EINGABEDATEI = os.path.join(BASIS_VERZEICHNIS, "..", "data", "jobs_scraped.csv")
AUSGABEDATEI = os.path.join(BASIS_VERZEICHNIS, "..", "data", "output_2.csv")

daten = pd.read_csv(EINGABEDATEI)
for spalte in ["titel", "firma", "ort", "link"]:
    daten[spalte] = daten[spalte].astype(str).apply(clean_text)

klassifiziert = klassifiziere_jobtitel(daten)
klassifiziert.to_csv(AUSGABEDATEI, index=False, encoding="utf-8")
print(f"✅ Gespeichert: {AUSGABEDATEI} mit allen Angeboten und Filterfeldern.")
