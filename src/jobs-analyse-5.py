import os
import sys
import time
import json
import pandas as pd
import spacy
from transformers import pipeline

# Importar funciones auxiliares
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test")))
from utils import (
    clean_text,
    filter_irrelevant_phrases,
    extract_sector_from_text,
    erkenne_technologien,
    get_logger
)

logger = get_logger("jobs-analyse-5")

# --------------------------
# Pfadkonfiguration
# --------------------------
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
DATEN_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "data", "grupos_fase4"))
EINGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "results_con_grupo.csv")
STATUS_DATEI = os.path.join(DATEN_VERZEICHNIS, "grupo_status.json")
AUSGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "analyzed_offers_optimized.csv")

# --------------------------
# NLP-Modelle laden
# --------------------------
print("🔄 Lade NLP-Modelle...")
logger.info("jobs-analyse-5,START,Lade NLP-Modelle")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except:
    from spacy.cli import download
    download("xx_ent_wiki_sm")
    nlp = spacy.load("xx_ent_wiki_sm")

ROLLEN_LABELS = [
    "Data Scientist", "Data Analyst", "ML Engineer", "Software Engineer",
    "DevOps", "BI Analyst", "Account Manager", "Key Account Manager",
    "Healthcare Staff", "Audit / Finance", "IT Internship", "Sales Manager"
]

# --------------------------
# Hilfsfunktionen
# --------------------------
def extrahiere_entitaeten(text):
    return list(set(ent.text for ent in nlp(text[:500]).ents if ent.label_ != ""))

def klassifiziere_rolle(text):
    gekuerzt = text[:250]
    ergebnis = classifier(gekuerzt, ROLLEN_LABELS, multi_label=True)
    return ergebnis["labels"][0] if ergebnis["scores"][0] > 0.5 else "Unspecified"

def lade_status():
    with open(STATUS_DATEI, "r", encoding="utf-8") as f:
        return json.load(f)

def speichere_status(status):
    with open(STATUS_DATEI, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=4, ensure_ascii=False)

def analysiere_gruppe(df_gruppe):
    ergebnisse = []
    for _, zeile in df_gruppe.iterrows():
        titel = zeile.get("titel", "")
        beschreibung = zeile.get("beschreibung", "")

        if not isinstance(titel, str):
            titel = ""
        if not isinstance(beschreibung, str):
            beschreibung = ""

        beschreibung_clean = filter_irrelevant_phrases(beschreibung)
        text_kombiniert = titel + " " + beschreibung_clean

        rolle = klassifiziere_rolle(text_kombiniert)
        technologien = erkenne_technologien(text_kombiniert)
        entitaeten = extrahiere_entitaeten(beschreibung_clean)
        branche = extract_sector_from_text(text_kombiniert)

        eintrag = zeile.to_dict()
        eintrag.update({
            "rolle_titel": rolle,
            "technologien_titel": technologien,
            "entitaeten_beschreibung": entitaeten,
            "branche_detected": branche
        })
        ergebnisse.append(eintrag)
    return pd.DataFrame(ergebnisse)

# --------------------------
# Hauptfunktion
# --------------------------
def analysiere_angebote_gruppenweise(debug=False):
    logger.info("jobs-analyse-5,START,Beginne gruppenweise Analyse")
    alle = pd.read_csv(EINGABEDATEI)
    status = lade_status()
    total = len(status)

    for gruppenname, eintrag in status.items():
        if eintrag["estado"] == "completado":
            continue

        gruppe_id = int(gruppenname.split("_")[1])
        print(f"\n🔍 Verarbeite {gruppenname} mit {eintrag['num_filas']} Einträgen")
        logger.info(f"jobs-analyse-5,INFO,Verarbeite {gruppenname} mit {eintrag['num_filas']} Einträgen")

        df_gruppe = alle[alle["grupo_id"] == gruppe_id].copy()
        if debug:
            df_gruppe = df_gruppe.head(2)

        t0_group = time.time()
        df_result = analysiere_gruppe(df_gruppe)

        if os.path.exists(AUSGABEDATEI):
            try:
                df_vorher = pd.read_csv(AUSGABEDATEI, usecols=["offer_id"])
                max_id = df_vorher["offer_id"].max()
                start_id = int(max_id) + 1
            except:
                start_id = 1
        else:
            start_id = 1

        df_result["offer_id"] = range(start_id, start_id + len(df_result))
        header = not os.path.exists(AUSGABEDATEI)
        df_result.to_csv(AUSGABEDATEI, mode="a", index=False, header=header, encoding="utf-8")

        status[gruppenname]["estado"] = "completado"
        speichere_status(status)

        # Calcular métricas de avance y duración
        duration_sec = round(time.time() - t0_group)
        mins, secs = divmod(duration_sec, 60)
        completados = sum(1 for v in status.values() if v["estado"] == "completado")
        porcentaje = round((completados / total) * 100, 1)

        resumen = (
            f"⏱ Dauer: {mins}m {secs}s | "
            f"📦 {completados}/{total} Gruppen abgeschlossen | "
            f"🕒 {porcentaje}% Fortschritt"
        )

        print(f"✅ Gruppe {gruppenname} abgeschlossen und gespeichert")
        print(resumen)
        logger.info(f"jobs-analyse-5,SUCCESS,{gruppenname} abgeschlossen – {resumen}")

        if debug:
            break

# --------------------------
# Direkter Aufruf
# --------------------------
if __name__ == "__main__":
    debug = "--debug" in sys.argv
    analysiere_angebote_gruppenweise(debug=debug)