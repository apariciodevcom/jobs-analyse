import os
import sys
import time
import pandas as pd
import spacy
from transformers import pipeline

# --------------------------
# Pfadkonfiguration
# --------------------------
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
TEST_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "test"))
DATEN_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "data"))
EINGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "results.csv")
AUSGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "analyzed_offers_optimized.csv")

sys.path.append(TEST_VERZEICHNIS)
from utils import clean_text

# --------------------------
# NLP-Modelle laden
# --------------------------
print("🔄 Lade NLP-Modelle...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except:
    from spacy.cli import download
    download("xx_ent_wiki_sm")
    nlp = spacy.load("xx_ent_wiki_sm")

ROLLEN_LABELS = ["Data Scientist", "Data Analyst", "Machine Learning Engineer", "Software Engineer",
                 "Business Analyst", "DevOps Engineer", "BI Analyst", "Data Engineer"]
STUFEN_LABELS = ["Intern", "Junior", "Senior", "Lead", "Unspecified"]
BRANCHEN_LABELS = ["Finance", "Healthcare", "Retail", "Telecommunications", "IT", "Education", "Government"]
TECH_STICHWÖRTER = ["python", "sql", "excel", "r", "tableau", "power bi", "cloud", "aws", "azure", "linux",
                    "pytorch", "tensorflow", "spark", "hadoop", "snowflake", "looker"]

# --------------------------
# Funktionen
# --------------------------
def extrahiere_entitaeten(text, debug=False):
    gekuerzt = text[:500]
    return list(set(ent.text for ent in nlp(gekuerzt).ents if ent.label_ != "")) if not debug else []

def erkenne_technologien(text):
    text_klein = text.lower()
    return [tech for tech in TECH_STICHWÖRTER if tech in text_klein]

def klassifiziere_textfeld(text, labels):
    gekuerzt = text[:1000]
    ergebnis = classifier(gekuerzt, labels, multi_label=True)
    label = ergebnis["labels"][0]
    score = ergebnis["scores"][0]
    return label if score > 0.5 else "Unspecified"

# --------------------------
# Hauptfunktion
# --------------------------
def analysiere_anzeigen_in_losen(batch_size=100, debug=False):
    alle = pd.read_csv(EINGABEDATEI)
    alle = alle.dropna(subset=["beschreibung"])
    alle["link"] = alle["link"].astype(str)
    alle["beschreibung"] = alle["beschreibung"].astype(str)

    for spalte in ["titel", "firma", "ort", "beschreibung"]:
        alle[spalte] = alle[spalte].astype(str).apply(clean_text)

    if os.path.exists(AUSGABEDATEI):
        bereits = pd.read_csv(AUSGABEDATEI)
        bearbeitet_links = set(bereits["link"].astype(str))
        verbleibend = alle[~alle["link"].isin(bearbeitet_links)]
    else:
        verbleibend = alle

    print(f"🔍 Noch zu analysieren: {len(verbleibend)} Stellenangebote.")

    for i in range(0, len(verbleibend), batch_size):
        batch = verbleibend.iloc[i:i + batch_size].copy()
        print(f"\n🧩 Bearbeite Batch {i // batch_size + 1} ({len(batch)} Angebote)...")

        rollen, stufen, branchen, technologien, entitaeten = [], [], [], [], []

        for j, zeile in batch.iterrows():
            text = zeile["beschreibung"]
            print(f"\n[{j+1}/{len(alle)}] {zeile['titel']}")

            t0 = time.time()
            rolle = klassifiziere_textfeld(text, ROLLEN_LABELS)
            stufe = klassifiziere_textfeld(text, STUFEN_LABELS)
            branche = klassifiziere_textfeld(text, BRANCHEN_LABELS)
            t1 = time.time()

            print(f"⏱ NLP-Klassifikation abgeschlossen in {t1 - t0:.2f} Sekunden")

            techs = erkenne_technologien(text)
            ents = extrahiere_entitaeten(text, debug=debug)

            rollen.append(rolle)
            stufen.append(stufe)
            branchen.append(branche)
            technologien.append(techs)
            entitaeten.append(ents)

        batch["rolle"] = rollen
        batch["stufe_nlp"] = stufen
        batch["branche"] = branchen
        batch["technologien"] = technologien
        batch["entitaeten"] = entitaeten

        header = not os.path.exists(AUSGABEDATEI)
        batch.to_csv(AUSGABEDATEI, mode="a", header=header, index=False, encoding="utf-8")
        print(f"✅ Batch gespeichert ({i + len(batch)} von {len(alle)})")

# --------------------------
# Direkter Aufruf
# --------------------------
if __name__ == "__main__":
    debug = "--debug" in sys.argv
    analysiere_anzeigen_in_losen(batch_size=100, debug=debug)
