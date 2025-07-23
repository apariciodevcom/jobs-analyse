import os
import sys
import time
import random
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# --------------------------
# Pfadkonfiguration
# --------------------------
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
TEST_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "test"))
DATEN_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "data"))
CHROMEDRIVER_PFAD = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "bin", "chromedriver.exe"))
EINGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "output_2.csv")
AUSGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "results.csv")

# utils importieren
sys.path.append(TEST_VERZEICHNIS)
from utils import clean_text

# --------------------------
# Browser initialisieren
# --------------------------
def browser_einrichten():
    optionen = Options()
    optionen.add_argument("--headless")
    optionen.add_argument("--disable-gpu")
    optionen.add_argument("--window-size=1920,1080")
    dienst = Service(executable_path=CHROMEDRIVER_PFAD)
    return webdriver.Chrome(service=dienst, options=optionen)

# --------------------------
# Detaildaten pro Stelle extrahieren
# --------------------------
def extrahiere_stellenbeschreibung(browser, url):
    try:
        browser.get(url)
        time.sleep(random.uniform(2.0, 3.5))

        def sicher_lesen(by, selector):
            try:
                return browser.find_element(by, selector).text.strip()
            except:
                return ""

        beschreibung = clean_text(sicher_lesen(By.CSS_SELECTOR, 'div[data-cy="vacancy-description"]'))
        publikationsdatum = clean_text(sicher_lesen(By.CSS_SELECTOR, "li[data-cy='info-publication'] span.white-space_nowrap"))
        pensum = clean_text(sicher_lesen(By.CSS_SELECTOR, "li[data-cy='info-workload'] span.white-space_nowrap"))
        vertragsart_detail = clean_text(sicher_lesen(By.CSS_SELECTOR, "li[data-cy='info-contract'] span.white-space_nowrap"))
        sprache = clean_text(sicher_lesen(By.CSS_SELECTOR, "li[data-cy='info-language'] span:not([class])"))
        arbeitsort = clean_text(sicher_lesen(By.CSS_SELECTOR, "li[data-cy='info-workplace'] span:not([class])"))

        return {
            "beschreibung": beschreibung,
            "publikationsdatum": publikationsdatum,
            "pensum": pensum,
            "vertragsart_detail": vertragsart_detail,
            "sprache": sprache,
            "arbeitsort": arbeitsort
        }

    except Exception as e:
        print(f"❌ Fehler beim Extrahieren der URL {url}: {e}")
        return None

# --------------------------
# Hauptfunktion
# --------------------------
def verarbeite_stellenangebote(debug=False):
    daten = pd.read_csv(EINGABEDATEI)
    daten = daten.dropna(subset=["link"])
    daten["link"] = daten["link"].str.strip()
    daten["link"] = daten["link"].str.replace("https://www.jobs.chhttps://www.jobs.ch", "https://www.jobs.ch")

    spalten = ["titel", "firma", "ort", "vertragsart", "stufe", "link"]
    for spalte in spalten:
        daten[spalte] = daten[spalte].astype(str).apply(clean_text)

    if debug:
        daten = daten.head(1)

    browser = browser_einrichten()
    ergebnisse = []

    start_time = time.time()
    gesamt = len(daten)
    fehler = 0

    try:
        for i, zeile in daten.iterrows():
            url = zeile["link"]
            print(f"\n[{i+1}/{gesamt}] Verarbeite URL:\n{url}")

            t0 = time.time()
            details = extrahiere_stellenbeschreibung(browser, url)
            dauer = time.time() - t0

            if details:
                job_text = details.get("beschreibung", "")
                pub_date = details.get("publikationsdatum", "")
                pensum = details.get("pensum", "")
                vertragsart_detail = details.get("vertragsart_detail", "")
                sprache = details.get("sprache", "")
                arbeitsort = details.get("arbeitsort", "")
                print(f"✅ Erfolgreich extrahiert in {dauer:.2f} Sekunden")
            else:
                job_text = pub_date = pensum = vertragsart_detail = sprache = arbeitsort = ""
                fehler += 1
                print(f"❌ Fehler beim Extrahieren ({fehler} insgesamt)")

            vergangen = time.time() - start_time
            durchschnitt = vergangen / (i + 1)
            verbleibend = durchschnitt * (gesamt - i - 1)
            eta = datetime.timedelta(seconds=int(verbleibend))
            print(f"⏱ Geschätzte verbleibende Zeit: {eta}")

            ergebnisse.append({
                "titel": zeile["titel"],
                "firma": zeile["firma"],
                "ort": zeile["ort"],
                "vertragsart": zeile.get("vertragsart", ""),
                "stufe": zeile.get("stufe", ""),
                "link": url,
                "publikationsdatum": pub_date,
                "pensum": pensum,
                "vertragsart_detail": vertragsart_detail,
                "sprache": sprache,
                "arbeitsort": arbeitsort,
                "beschreibung": job_text
            })

    finally:
        browser.quit()

    df_resultat = pd.DataFrame(ergebnisse)
    df_resultat.to_csv(AUSGABEDATEI, index=False, encoding="utf-8")
    print(f"\n✅ Fertig. {len(df_resultat)} Einträge gespeichert in '{AUSGABEDATEI}'")
    print(f"⚠️ Fehler insgesamt: {fehler}")

# --------------------------
# Direkter Aufruf
# --------------------------
if __name__ == "__main__":
    verarbeite_stellenangebote(debug=False)
