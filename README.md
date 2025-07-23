# Jobs Analyse St. Gallen

Automatisierte Analyse von Stellenangeboten in der Ostschweiz (Region St. Gallen).  
Dieses Projekt dient ausschließlich persönlichen Zwecken zur Entscheidungsunterstützung bei der Jobsuche.

## Überblick

Das Projekt führt einen mehrstufigen Scraping- und Analyseprozess durch:

1. **Scraping der Jobliste** (`jobs-analyse-1.py`):  
   Ruft bis zu 100 Seiten von jobs.ch (Region St. Gallen/Appenzell) ab und speichert grundlegende Informationen (Titel, Firma, Ort, Link) in `jobs_scraped.csv`.

2. **Vorfilterung und Klassifikation** (`jobs-analyse-2.py`):  
   Setzt Filter auf Basis von Titel (Ausschlusskriterien, Senioritätsstufen, Tech-Schlüsselwörter) und identifiziert relevante Angebote. Ausgabe: `output_2.csv`.

3. **Extraktion des Volltexts der Anzeigen** (`jobs-analyse-3.py`):  
   Lädt jede Anzeige individuell per Selenium, extrahiert Beschreibungstext, Arbeitsort, Vertragstyp, Sprachen etc. Ausgabe: `results.csv`.

4. **Semantische Analyse mittels NLP** (`jobs-analyse-4.py`):  
   Nutzt Transformers (Zero-shot-classification mit BART) zur Klassifikation nach Rolle, Senioritätsstufe und Branche. Zusätzlich:
   - Entity Recognition via spaCy
   - Keyword-Matching zur Identifikation von Technologien
   - Ausgabe: `analyzed_offers_optimized.csv`

## Dateistruktur

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── verzeichnisstruktur.txtgit rm estructura.txt
├── bin/
│   └── chromedriver.exe
├── data/
│   ├── jobs_scraped.csv
│   ├── output_2.csv
│   ├── results.csv
│   ├── analyzed_offers_optimized.csv
│   └── ... (weitere CSV-Dateien)
├── analysis/
│   ├── results.xlsx
│   ├── analyzed_offers.xlsx
│   └── ...
├── jobs-analyse-1.py
├── jobs-analyse-2.py
├── jobs-analyse-3.py
├── jobs-analyse-4.py
└── utils.py
```

## Anforderungen

### Installation

```bash
pip install -r requirements.txt
```

### Notwendige Bibliotheken

- `pandas`
- `selenium`
- `spacy`
- `transformers`
- `torch`
- `sentencepiece`
- `scikit-learn` *(optional für weiterführende Analysen)*

Der Chrome WebDriver (`chromedriver.exe`) wird im Verzeichnis `bin/` erwartet.

## Verwendung des NLP-Moduls

Das Skript `jobs-analyse-4.py` führt eine erweiterte Textanalyse durch:

- **Zero-Shot-Classification** mit `facebook/bart-large-mnli`:
  - Erkennt berufliche Rolle (z.B. Data Analyst, ML Engineer)
  - Schätzt Senioritätsniveau (Intern, Junior, Senior etc.)
  - Bestimmt Industrie (IT, Finance, etc.)

- **Entity Recognition (spaCy multilingual)**:
  - Extrahiert relevante Entitäten (Firmen, Orte, Technologien)

- **Technologie-Erkennung**:
  - Durch Keyword-Matching: Python, SQL, Azure, etc.

Optional kann ein `--debug`-Flag zur Reduktion der Laufzeit verwendet werden.

## Rechtlicher Hinweis & Datenschutz

- Dieses Projekt dient ausschließlich **privaten und persönlichen Zwecken**.
- Es werden **keine Daten an Dritte weitergegeben**, verkauft oder veröffentlicht.
- Die analysierten Daten stammen aus öffentlich zugänglichen Quellen (jobs.ch).
- Alle Anfragen erfolgen mit angemessenen Wartezeiten, um Serverlast zu vermeiden.
- Das Projekt verstößt **nicht gegen Geschäftsbedingungen**, da keine API verwendet wird und nur öffentlich sichtbare Daten gesammelt werden.
- Falls jobs.ch oder eine betroffene Partei Einwände gegen dieses Projekt erhebt, wird der Betrieb unverzüglich eingestellt.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.  
Die Nutzung erfolgt auf eigenes Risiko. Der Autor übernimmt keine Haftung für etwaige rechtliche oder technische Folgen.
