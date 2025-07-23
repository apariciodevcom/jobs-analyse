import os
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --------------------------
# Pfadkonfiguration
# --------------------------
BASIS_VERZEICHNIS = os.path.dirname(os.path.abspath(__file__))
TEST_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "test"))
DATEN_VERZEICHNIS = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "data"))
CHROMEDRIVER_PFAD = os.path.abspath(os.path.join(BASIS_VERZEICHNIS, "..", "bin", "chromedriver.exe"))
AUSGABEDATEI = os.path.join(DATEN_VERZEICHNIS, "jobs_scraped.csv")

sys.path.append(TEST_VERZEICHNIS)
from utils import clean_text, get_logger

logger = get_logger("jobs-analyse-1")

# --------------------------
# Initialisierung des Browsers
# --------------------------
def browser_einrichten():
    optionen = Options()
    optionen.add_argument("--headless")
    optionen.add_argument("--disable-gpu")
    optionen.add_argument("--window-size=1920,1080")
    dienst = Service(executable_path=CHROMEDRIVER_PFAD)
    return webdriver.Chrome(service=dienst, options=optionen)

# --------------------------
# Scraping-Logik
# --------------------------
def jobs_abrufen(browser, max_seiten=100):
    basis_url = "https://www.jobs.ch/de/stellenangebote/?page={page}&region=21&term="
    ergebnisse = []

    for seite in range(1, max_seiten + 1):
        url = basis_url.format(page=seite)
        print(f"\nLade Seite {seite} → {url}")
        logger.info(f"jobs-analyse-1,INFO,Lade Seite {seite} → {url}")
        browser.get(url)
        time.sleep(2.5)

        angebote = browser.find_elements(By.CSS_SELECTOR, "a[data-cy='job-link']")
        print(f"→ {len(angebote)} Stellenangebote gefunden")
        logger.info(f"jobs-analyse-1,INFO,{len(angebote)} Angebote auf Seite {seite} gefunden")

        for angebot in angebot:
            try:
                titel = angebot.get_attribute("title").strip()
                href = angebot.get_attribute("href").strip()
                link = href if href.startswith("http") else "https://www.jobs.ch" + href
            except Exception as e:
                titel = link = ""
                logger.warning(f"jobs-analyse-1,WARN,Fehler beim Parsen eines Angebots: {e}")

            firma = ""
            ort = ""
            try:
                p_tags = angebot.find_elements(By.CSS_SELECTOR, "p.textStyle_p2")
                for p in p_tags:
                    text = p.text.strip()
                    if p.find_elements(By.TAG_NAME, "strong") and not firma:
                        firma = text
                    elif (
                        not p.find_elements(By.TAG_NAME, "strong")
                        and not any(w in text.lower() for w in ["vor", "heute", "gestern"])
                        and not ort
                    ):
                        ort = text
            except Exception as e:
                logger.warning(f"jobs-analyse-1,WARN,Fehler beim Extrahieren von Firma/Ort: {e}")

            ergebnisse.append({
                "titel": titel,
                "ort": ort,
                "firma": firma,
                "link": link
            })

        print(f"→ Insgesamt gesammelt: {len(ergebnisse)} Angebote")
        logger.info(f"jobs-analyse-1,INFO,Bisher insgesamt gesammelt: {len(ergebnisse)} Angebote")

    return ergebnisse

# --------------------------
# Hauptprogramm
# --------------------------
if __name__ == "__main__":
    logger.info("jobs-analyse-1,START,Beginne Scraping-Prozess")
    browser = browser_einrichten()
    try:
        jobs = jobs_abrufen(browser, max_seiten=100)
        df = pd.DataFrame(jobs)
        for spalte in ["titel", "ort", "firma", "link"]:
            df[spalte] = df[spalte].apply(clean_text)
        df.to_csv(AUSGABEDATEI, index=False, encoding="utf-8")
        print(f"\n✅ Gespeichert: {len(df)} Stellenangebote in '{AUSGABEDATEI}'")
        logger.info(f"jobs-analyse-1,SUCCESS,{len(df)} Stellenangebote gespeichert in {AUSGABEDATEI}")
    except Exception as e:
        logger.error(f"jobs-analyse-1,ERROR,Fehler im Hauptprogramm: {e}")
    finally:
        browser.quit()
        logger.info("jobs-analyse-1,END,Browser geschlossen und Skript beendet")
