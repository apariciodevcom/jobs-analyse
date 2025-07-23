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

# Sicherstellen, dass 'test' im sys.path enthalten ist, um utils zu importieren
sys.path.append(TEST_VERZEICHNIS)
from utils import clean_text

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
# Grundlegendes Scraping der Stellenangebote
# --------------------------
def jobs_abrufen(browser, max_seiten=100):
    basis_url = "https://www.jobs.ch/en/vacancies/?page={page}&region=21&term="
    ergebnisse = []

    for seite in range(1, max_seiten + 1):
        url = basis_url.format(page=seite)
        print(f"\nLade Seite {seite} → {url}")
        browser.get(url)
        time.sleep(2.5)

        angebote = browser.find_elements(By.CSS_SELECTOR, "a[data-cy='job-link']")
        print(f"→ {len(angebote)} Stellenangebote gefunden")

        for angebot in angebote:
            try:
                titel = angebot.get_attribute("title").strip()
                href = angebot.get_attribute("href").strip()
                link = href if href.startswith("http") else "https://www.jobs.ch" + href
            except:
                titel = link = ""

            try:
                absätze = angebot.find_elements(By.CSS_SELECTOR, "p.textStyle_p2")
                ort = firma = ""
                for absatz in absätze:
                    if absatz.find_elements(By.TAG_NAME, "strong"):
                        firma = absatz.text.strip()
                    else:
                        ort = absatz.text.strip()
            except:
                ort = firma = ""

            ergebnisse.append({
                "titel": titel,
                "firma": firma,
                "ort": ort,
                "link": link
            })

        print(f"→ Insgesamt gesammelt: {len(ergebnisse)} Angebote")

    return ergebnisse

# --------------------------
# Hauptprogramm
# --------------------------
if __name__ == "__main__":
    browser = browser_einrichten()
    try:
        jobs = jobs_abrufen(browser, max_seiten=100)
        df = pd.DataFrame(jobs)
        for spalte in ["titel", "firma", "ort", "link"]:
            df[spalte] = df[spalte].apply(clean_text)
        df.to_csv(AUSGABEDATEI, index=False, encoding="utf-8")
        print(f"\n✅ Gespeichert: {len(df)} Stellenangebote in '{AUSGABEDATEI}'")
    finally:
        browser.quit()
